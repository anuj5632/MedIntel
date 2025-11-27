from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """Incoming sensor payload."""

    equipment_id: str = Field(..., example="MRI-01")
    temperature: float = Field(..., example=68.2)
    pressure: float = Field(..., example=1.8)
    vibration: Optional[float] = Field(default=None, example=0.02)


class PredictionResponse(BaseModel):
    """Prediction response returned to clients."""

    equipment_id: str
    anomaly_score: float = Field(..., description="Probability-like anomaly score between 0 and 1")
    is_failure_risk: bool
    maintenance_warning: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
