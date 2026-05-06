from django.db import models


class DetectionRecord(models.Model):
    FILE_TYPES = [
        ("video", "Video"),
        ("audio", "Audio"),
        ("image", "Image"),
    ]
    VERDICTS = [
        ("real", "Real"),
        ("fake", "Fake"),
        ("uncertain", "Uncertain"),
    ]

    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=16, choices=FILE_TYPES)
    file_path = models.FileField(upload_to="uploads/")
    verdict = models.CharField(max_length=16, choices=VERDICTS)
    confidence_score = models.FloatField()
    facial_inconsistency = models.FloatField(null=True, blank=True)
    audio_sync_score = models.FloatField(null=True, blank=True)
    compression_artifacts = models.FloatField(null=True, blank=True)
    gan_fingerprint = models.FloatField(null=True, blank=True)
    ai_explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time_ms = models.IntegerField()
    metadata_blob = models.TextField(blank=True, default="{}")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.file_name} ({self.verdict})"


class AnalyticsSummary(models.Model):
    date = models.DateField(unique=True)
    total_scans = models.IntegerField(default=0)
    fake_count = models.IntegerField(default=0)
    real_count = models.IntegerField(default=0)
    avg_confidence = models.FloatField(default=0.0)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} - {self.total_scans} scans"
