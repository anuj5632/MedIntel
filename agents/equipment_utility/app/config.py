from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Runtime configuration values for the Equipment & Utility Agent."""

    base_dir: Path = Path(__file__).resolve().parent.parent
    model_dir: Path = base_dir / "models"
    model_path: Path = model_dir / "isolation_forest.joblib"
    scaler_path: Path = model_dir / "scaler.joblib"
    calibration_path: Path = model_dir / "calibration.json"
    data_path: Path = base_dir / "data" / "mock_iot_logs.csv"
    features: tuple[str, ...] = ("temperature", "pressure", "vibration")
    anomaly_threshold: float = 0.65  # probability-like threshold for maintenance warning


_settings = Settings()


def get_settings() -> Settings:
    """Return cached settings instance."""

    return _settings
