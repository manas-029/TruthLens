from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnalyticsSummary",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(unique=True)),
                ("total_scans", models.IntegerField(default=0)),
                ("fake_count", models.IntegerField(default=0)),
                ("real_count", models.IntegerField(default=0)),
                ("avg_confidence", models.FloatField(default=0.0)),
            ],
            options={"ordering": ["-date"]},
        ),
        migrations.CreateModel(
            name="DetectionRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file_name", models.CharField(max_length=255)),
                ("file_type", models.CharField(choices=[("video", "Video"), ("audio", "Audio"), ("image", "Image")], max_length=16)),
                ("file_path", models.FileField(upload_to="uploads/")),
                ("verdict", models.CharField(choices=[("real", "Real"), ("fake", "Fake"), ("uncertain", "Uncertain")], max_length=16)),
                ("confidence_score", models.FloatField()),
                ("facial_inconsistency", models.FloatField(blank=True, null=True)),
                ("audio_sync_score", models.FloatField(blank=True, null=True)),
                ("compression_artifacts", models.FloatField(blank=True, null=True)),
                ("gan_fingerprint", models.FloatField(blank=True, null=True)),
                ("ai_explanation", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("processing_time_ms", models.IntegerField()),
                ("metadata_blob", models.TextField(blank=True, default="{}")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
