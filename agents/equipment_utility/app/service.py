from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from .config import Settings, get_settings
from .models import PredictionResponse, SensorReading

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PredictionService:
    """Service responsible for equipment anomaly scoring."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._scaler: Optional[StandardScaler] = None
        self._model: Optional[IsolationForest] = None
        self._calibration: Optional[dict[str, float]] = None
        self.prediction_count: int = 0
        self._load_artifacts()

    # ------------------------------------------------------------------
    def _load_artifacts(self) -> None:
        """Load trained scaler and model from disk."""

        logger.info("Loading scaler from %s", self.settings.scaler_path)
        logger.info("Loading model from %s", self.settings.model_path)

        self._scaler = self._load_joblib(self.settings.scaler_path, StandardScaler)
        self._model = self._load_joblib(self.settings.model_path, IsolationForest)
        self._calibration = self._load_calibration(self.settings.calibration_path)

    @staticmethod
    def _load_joblib(path: Path, expected_type: type) -> object:
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found at {path}")
        artifact = joblib.load(path)
        if not isinstance(artifact, expected_type):
            raise TypeError(f"Artifact at {path} is not {expected_type.__name__}")
        return artifact

    @staticmethod
    def _load_calibration(path: Path) -> Optional[dict[str, float]]:
        if not path.exists():
            logger.warning("Calibration metadata not found at %s; using sigmoid fallback", path)
            return None
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        required = {"score_min", "score_max", "score_mean", "score_std"}
        if not required.issubset(data):
            logger.warning("Calibration metadata missing keys %s; using sigmoid fallback", required - set(data))
            return None
        return {key: float(value) for key, value in data.items()}

    # ------------------------------------------------------------------
    def predict(self, reading: SensorReading) -> PredictionResponse:
        if self._model is None or self._scaler is None:
            raise RuntimeError("Model artifacts are not loaded")

        features = self._build_feature_vector(reading)
        scaled = self._scaler.transform(features)
        anomaly_raw = float(-self._model.score_samples(scaled)[0])
        anomaly_prob = self._scale_score(anomaly_raw)

        is_failure = anomaly_prob >= self.settings.anomaly_threshold
        warning = (
            "High risk: schedule immediate inspection"
            if is_failure
            else "Normal operation"
        )

        self.prediction_count += 1

        return PredictionResponse(
            equipment_id=reading.equipment_id,
            anomaly_score=float(anomaly_prob),
            is_failure_risk=is_failure,
            maintenance_warning=warning,
        )

    # ------------------------------------------------------------------
    def _build_feature_vector(self, reading: SensorReading) -> np.ndarray:
        vibration = reading.vibration if reading.vibration is not None else 0.0
        vector = np.array(
            [[reading.temperature, reading.pressure, vibration]],
            dtype=np.float64,
        )
        return vector

    def _scale_score(self, raw_score: float) -> float:
        if self._calibration:
            score_mean = self._calibration["score_mean"]
            score_std = max(self._calibration["score_std"], 1e-9)
            z_score = (raw_score - score_mean) / score_std
            return self._to_float(self._sigmoid(z_score))

        return self._to_float(self._sigmoid(raw_score))

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1 / (1 + math.exp(-value))

    @staticmethod
    def _to_float(value: float | np.ndarray) -> float:
        if isinstance(value, np.ndarray):
            if value.size != 1:
                raise ValueError("Sigmoid produced unexpected vector output")
            return float(value.item())
        return float(value)


__all__ = ["PredictionService"]
