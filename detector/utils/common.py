import random
from pathlib import Path

from PIL import Image


def clamp(value, min_value=0.0, max_value=100.0):
    return max(min_value, min(max_value, round(value, 1)))


def choose_verdict(confidence):
    if confidence >= 72:
        return "fake"
    if confidence <= 42:
        return "real"
    return "uncertain"


def explain_signal(media_type, verdict, metrics):
    strongest_key = max(metrics, key=metrics.get)
    labels = {
        "facial_inconsistency": "facial consistency drift",
        "audio_sync_score": "audio synchronization irregularity",
        "compression_artifacts": "compression artifact density",
        "gan_fingerprint": "GAN fingerprint residue",
    }
    strongest_label = labels.get(strongest_key, "forensic anomaly")
    if verdict == "fake":
        return (
            f"TruthLens identified elevated {strongest_label} signals in this {media_type} sample. "
            "The combined forensic pattern is consistent with AI-assisted manipulation rather than organic capture."
        )
    if verdict == "real":
        return (
            f"TruthLens found low-risk {strongest_label} indicators and a stable integrity profile for this {media_type}. "
            "No dominant manipulation signature was detected during the current scan."
        )
    return (
        f"TruthLens observed mixed evidence led by {strongest_label}. "
        f"This {media_type} should be reviewed manually because the signal profile is suggestive but not decisive."
    )


def extract_image_metadata(file_path):
    path = Path(file_path)
    metadata = {
        "file_size": path.stat().st_size if path.exists() else 0,
        "duration": None,
        "resolution": "Unknown",
        "codec": "N/A",
        "creation_date": None,
    }
    try:
        with Image.open(file_path) as img:
            metadata["resolution"] = f"{img.width}x{img.height}"
    except Exception:
        pass
    return metadata


def weighted_metric(base, spread):
    return clamp(random.uniform(base - spread, base + spread))
