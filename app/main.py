from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from .config import get_settings
from .models import PredictionResponse, SensorReading
from .service import PredictionService

app = FastAPI(
    title="Equipment & Utility Agent",
    description="Predict equipment failure risk from IoT telemetry.",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event() -> None:
    app.state.prediction_service = PredictionService(get_settings())


def get_service() -> PredictionService:
    service: PredictionService | None = getattr(app.state, "prediction_service", None)
    if service is None:
        service = PredictionService(get_settings())
        app.state.prediction_service = service
    return service


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics/basic")
def metrics(service: PredictionService = Depends(get_service)) -> dict[str, int]:
    return {"predictions_total": service.prediction_count}


@app.post("/predict", response_model=PredictionResponse)
def predict(
    payload: SensorReading,
    service: PredictionService = Depends(get_service),
) -> PredictionResponse:
    try:
        return service.predict(payload)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
