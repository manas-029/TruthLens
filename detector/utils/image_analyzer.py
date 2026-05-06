import random

from .common import choose_verdict, explain_signal, extract_image_metadata, weighted_metric


def analyze_image(file_path):
    seed_bias = random.choice([28, 41, 63, 77, 86])
    facial_inconsistency = weighted_metric(seed_bias, 18)
    compression_artifacts = weighted_metric(seed_bias + 8, 16)
    gan_fingerprint = weighted_metric(seed_bias + 4, 20)
    confidence = round((facial_inconsistency * 0.34) + (compression_artifacts * 0.31) + (gan_fingerprint * 0.35), 1)
    verdict = choose_verdict(confidence)
    metrics = {
        "facial_inconsistency": facial_inconsistency,
        "compression_artifacts": compression_artifacts,
        "gan_fingerprint": gan_fingerprint,
    }
    return {
        "verdict": verdict,
        "confidence": confidence,
        "facial_inconsistency": facial_inconsistency,
        "audio_sync_score": None,
        "compression_artifacts": compression_artifacts,
        "gan_fingerprint": gan_fingerprint,
        "explanation": explain_signal("image", verdict, metrics),
        "metadata": extract_image_metadata(file_path),
    }
