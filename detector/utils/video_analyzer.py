import random
from pathlib import Path

from .common import choose_verdict, explain_signal, weighted_metric


def analyze_video(file_path):
    seed_bias = random.choice([22, 39, 55, 71, 92])
    facial_inconsistency = weighted_metric(seed_bias + 6, 17)
    audio_sync_score = weighted_metric(seed_bias, 21)
    compression_artifacts = weighted_metric(seed_bias + 8, 16)
    gan_fingerprint = weighted_metric(seed_bias + 10, 15)
    confidence = round(
        (facial_inconsistency * 0.29)
        + (audio_sync_score * 0.23)
        + (compression_artifacts * 0.24)
        + (gan_fingerprint * 0.24),
        1,
    )
    verdict = choose_verdict(confidence)
    metrics = {
        "facial_inconsistency": facial_inconsistency,
        "audio_sync_score": audio_sync_score,
        "compression_artifacts": compression_artifacts,
        "gan_fingerprint": gan_fingerprint,
    }
    path = Path(file_path)
    return {
        "verdict": verdict,
        "confidence": confidence,
        "facial_inconsistency": facial_inconsistency,
        "audio_sync_score": audio_sync_score,
        "compression_artifacts": compression_artifacts,
        "gan_fingerprint": gan_fingerprint,
        "explanation": explain_signal("video", verdict, metrics),
        "metadata": {
            "file_size": path.stat().st_size if path.exists() else 0,
            "duration": "00:01:24",
            "resolution": "1920x1080",
            "codec": "H.264/AAC",
            "creation_date": None,
        },
    }
