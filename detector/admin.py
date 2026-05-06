from django.contrib import admin

from .models import AnalyticsSummary, DetectionRecord


@admin.register(DetectionRecord)
class DetectionRecordAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "file_type",
        "verdict",
        "confidence_score",
        "created_at",
    )
    list_filter = ("file_type", "verdict", "created_at")
    search_fields = ("file_name", "ai_explanation")


@admin.register(AnalyticsSummary)
class AnalyticsSummaryAdmin(admin.ModelAdmin):
    list_display = ("date", "total_scans", "fake_count", "real_count", "avg_confidence")
