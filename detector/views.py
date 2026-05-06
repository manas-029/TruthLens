import csv
import json
import time
from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from .models import AnalyticsSummary, DetectionRecord
from .serializers import DetectionRecordSerializer
from .utils.audio_analyzer import analyze_audio
from .utils.image_analyzer import analyze_image
from .utils.video_analyzer import analyze_video


def index(request):
    return render(request, "index.html")


def dashboard(request):
    return render(request, "dashboard.html")


def history_page(request):
    records = DetectionRecord.objects.all()
    paginator = Paginator(records, 8)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "history.html", {"page_obj": page})


def analytics_page(request):
    return render(request, "analytics.html")


def result_page(request, record_id):
    record = get_object_or_404(DetectionRecord, pk=record_id)
    serialized = DetectionRecordSerializer(record, context={"request": request}).data
    metadata = getattr(record, "metadata_blob", None)
    return render(
        request,
        "result.html",
        {
            "record": record,
            "record_json": json.dumps(serialized),
            "metadata": json.loads(metadata) if metadata else {},
        },
    )


def update_daily_summary(record):
    date = timezone.localdate(record.created_at)
    day_records = DetectionRecord.objects.filter(created_at__date=date)
    summary, _ = AnalyticsSummary.objects.get_or_create(date=date)
    summary.total_scans = day_records.count()
    summary.fake_count = day_records.filter(verdict="fake").count()
    summary.real_count = day_records.filter(verdict="real").count()
    summary.avg_confidence = round(day_records.aggregate(avg=Avg("confidence_score"))["avg"] or 0.0, 1)
    summary.save()


def analyzer_for(file_type):
    return {
        "video": analyze_video,
        "audio": analyze_audio,
        "image": analyze_image,
    }[file_type]


@require_http_methods(["POST"])
def detect_api(request):
    upload = request.FILES.get("file")
    file_type = request.POST.get("file_type")
    if not upload or file_type not in {"video", "audio", "image"}:
        return JsonResponse({"error": "Valid file and file_type are required."}, status=400)

    start = time.perf_counter()
    record = DetectionRecord.objects.create(
        file_name=upload.name,
        file_type=file_type,
        file_path=upload,
        verdict="uncertain",
        confidence_score=0.0,
        ai_explanation="Pending analysis.",
        processing_time_ms=0,
    )

    analyzer = analyzer_for(file_type)
    analysis = analyzer(record.file_path.path)
    record.verdict = analysis["verdict"]
    record.confidence_score = analysis["confidence"]
    record.facial_inconsistency = analysis.get("facial_inconsistency")
    record.audio_sync_score = analysis.get("audio_sync_score")
    record.compression_artifacts = analysis.get("compression_artifacts")
    record.gan_fingerprint = analysis.get("gan_fingerprint")
    record.ai_explanation = analysis["explanation"]
    record.processing_time_ms = int((time.perf_counter() - start) * 1000)
    record.metadata_blob = json.dumps(analysis.get("metadata", {}))
    record.save()

    update_daily_summary(record)
    payload = DetectionRecordSerializer(record, context={"request": request}).data
    payload["metadata"] = analysis.get("metadata", {})
    payload["detail_url"] = request.build_absolute_uri(f"/result/{record.id}/")
    return JsonResponse(payload)


@require_GET
def history_api(request):
    queryset = DetectionRecord.objects.all()
    file_type = request.GET.get("type")
    verdict = request.GET.get("verdict")
    query = request.GET.get("q")

    if file_type in {"video", "audio", "image"}:
        queryset = queryset.filter(file_type=file_type)
    if verdict in {"real", "fake", "uncertain"}:
        queryset = queryset.filter(verdict=verdict)
    if query:
        queryset = queryset.filter(Q(file_name__icontains=query) | Q(ai_explanation__icontains=query))

    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    data = DetectionRecordSerializer(page_obj.object_list, many=True, context={"request": request}).data
    return JsonResponse(
        {
            "results": data,
            "pagination": {
                "page": page_obj.number,
                "pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "count": paginator.count,
            },
        }
    )


@require_GET
def analytics_live_api(request):
    today = timezone.localdate()
    records = DetectionRecord.objects.all()
    total = records.count()
    fake_count = records.filter(verdict="fake").count()
    real_count = records.filter(verdict="real").count()
    today_count = records.filter(created_at__date=today).count()
    accuracy_rate = round((real_count / total) * 100, 1) if total else 0.0
    live_feed = list(
        records.values("id", "file_name", "file_type", "verdict", "confidence_score", "created_at")[:10]
    )
    return JsonResponse(
        {
            "total_scans": total,
            "deepfakes_found": fake_count,
            "authentics": real_count,
            "accuracy_rate": accuracy_rate,
            "today_count": today_count,
            "live_feed": live_feed,
        }
    )


@require_GET
def analytics_chart_api(request):
    today = timezone.localdate()
    labels = []
    totals = []
    fake_series = []
    real_series = []
    for days_ago in range(29, -1, -1):
        day = today - timedelta(days=days_ago)
        day_records = DetectionRecord.objects.filter(created_at__date=day)
        labels.append(day.strftime("%b %d"))
        totals.append(day_records.count())
        fake_series.append(day_records.filter(verdict="fake").count())
        real_series.append(day_records.filter(verdict="real").count())

    by_type = DetectionRecord.objects.values("file_type").annotate(total=Count("id"))
    type_breakdown = {"video": 0, "audio": 0, "image": 0}
    for item in by_type:
        type_breakdown[item["file_type"]] = item["total"]

    confidence_buckets = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
    for score in DetectionRecord.objects.values_list("confidence_score", flat=True):
        if score <= 25:
            confidence_buckets["0-25"] += 1
        elif score <= 50:
            confidence_buckets["26-50"] += 1
        elif score <= 75:
            confidence_buckets["51-75"] += 1
        else:
            confidence_buckets["76-100"] += 1

    threat_map = [
        {"label": "Face Swap", "intensity": DetectionRecord.objects.filter(file_type="video", verdict="fake").count()},
        {"label": "Voice Clone", "intensity": DetectionRecord.objects.filter(file_type="audio", verdict="fake").count()},
        {"label": "Synthetic Portrait", "intensity": DetectionRecord.objects.filter(file_type="image", verdict="fake").count()},
        {"label": "Metadata Drift", "intensity": DetectionRecord.objects.filter(verdict="uncertain").count()},
    ]

    return JsonResponse(
        {
            "labels": labels,
            "detections_over_time": totals,
            "fake_series": fake_series,
            "real_series": real_series,
            "type_breakdown": type_breakdown,
            "confidence_distribution": confidence_buckets,
            "threat_map": threat_map,
        }
    )


@require_GET
def result_api(request, record_id):
    record = get_object_or_404(DetectionRecord, pk=record_id)
    payload = DetectionRecordSerializer(record, context={"request": request}).data
    payload["metadata"] = json.loads(record.metadata_blob) if getattr(record, "metadata_blob", None) else {}
    payload["detail_url"] = request.build_absolute_uri(f"/result/{record.id}/")
    return JsonResponse(payload)


@require_GET
def export_csv_api(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="truthlens-history.csv"'
    writer = csv.writer(response)
    writer.writerow(["File Name", "Type", "Verdict", "Confidence", "Date", "Processing Time (ms)"])
    for record in DetectionRecord.objects.all():
        writer.writerow(
            [
                record.file_name,
                record.file_type,
                record.verdict,
                record.confidence_score,
                timezone.localtime(record.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                record.processing_time_ms,
            ]
        )
    return response
