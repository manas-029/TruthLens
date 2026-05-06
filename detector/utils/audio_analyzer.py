import random
from pathlib import Path

from .common import choose_verdict, explain_signal, weighted_metric


def analyze_audio(file_path):
    seed_bias = random.choice([25, 36, 58, 74, 89])
    audio_sync_score = weighted_metric(seed_bias + 10, 20)
    compression_artifacts = weighted_metric(seed_bias - 4, 18)
    gan_fingerprint = weighted_metric(seed_bias + 6, 19)
    confidence = round((audio_sync_score * 0.45) + (compression_artifacts * 0.25) + (gan_fingerprint * 0.30), 1)
    verdict = choose_verdict(confidence)
    metrics = {
        "audio_sync_score": audio_sync_score,
        "compression_artifacts": compression_artifacts,
        "gan_fingerprint": gan_fingerprint,
    }
    path = Path(file_path)
    return {
        "verdict": verdict,
        "confidence": confidence,
        "facial_inconsistency": None,
        "audio_sync_score": audio_sync_score,
        "compression_artifacts": compression_artifacts,
        "gan_fingerprint": gan_fingerprint,
        "explanation": explain_signal("audio", verdict, metrics),
        "metadata": {
            "file_size": path.stat().st_size if path.exists() else 0,
            "duration": "00:00:18",
            "resolution": "Audio only",
            "codec": "PCM/WAV",
            "creation_date": None,
        },
    }
