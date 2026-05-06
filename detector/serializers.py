from rest_framework import serializers

from .models import AnalyticsSummary, DetectionRecord


class DetectionRecordSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    verdict_label = serializers.CharField(source="get_verdict_display", read_only=True)

    class Meta:
        model = DetectionRecord
        fields = [
            "id",
            "file_name",
            "file_type",
            "file_path",
            "file_url",
            "verdict",
            "verdict_label",
            "confidence_score",
            "facial_inconsistency",
            "audio_sync_score",
            "compression_artifacts",
            "gan_fingerprint",
            "ai_explanation",
            "created_at",
            "processing_time_ms",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if not obj.file_path:
            return None
        url = obj.file_path.url
        return request.build_absolute_uri(url) if request else url


class AnalyticsSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSummary
        fields = "__all__"
