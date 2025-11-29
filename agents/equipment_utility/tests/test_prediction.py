from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pytest
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.config import Settings
from app.models import SensorReading
from app.service import PredictionService


@pytest.fixture()
def service(tmp_path: Path) -> PredictionService:
    data = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    scaler = StandardScaler().fit(data)
    model = IsolationForest(random_state=0).fit(data)

    model_path = tmp_path / "model.joblib"
    scaler_path = tmp_path / "scaler.joblib"
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    settings = Settings(
        base_dir=Path("."),
        model_dir=tmp_path,
        model_path=model_path,
        scaler_path=scaler_path,
        data_path=Path("data/mock_iot_logs.csv"),
        features=("temperature", "pressure", "vibration"),
        anomaly_threshold=0.5,
    )

    return PredictionService(settings)


def test_prediction_response_contains_fields(service: PredictionService) -> None:
    reading = SensorReading(
        equipment_id="MRI-01",
        temperature=65.0,
        pressure=1.8,
        vibration=0.02,
    )

    response = service.predict(reading)

    assert response.equipment_id == "MRI-01"
    assert 0.0 <= response.anomaly_score <= 1.0
    assert response.maintenance_warning in {"Normal operation", "High risk: schedule immediate inspection"}
    assert service.prediction_count == 1


def test_high_anomaly_triggers_warning(service: PredictionService, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(PredictionService, "_sigmoid", staticmethod(lambda values: np.array([0.99])))

    reading = SensorReading(
        equipment_id="MRI-02",
        temperature=90.0,
        pressure=2.7,
        vibration=0.2,
    )

    response = service.predict(reading)

    assert response.is_failure_risk is True
    assert "High risk" in response.maintenance_warning
