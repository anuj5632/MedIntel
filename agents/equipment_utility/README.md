# Equipment & Utility Agent (Agent 4)

Predictive maintenance service for hospital equipment. It ingests IoT-style sensor readings, detects anomalies with Isolation Forest, and surfaces JSON maintenance warnings through a FastAPI service.

## Features
- 📈 Isolation Forest anomaly detection on temperature, pressure, and vibration signals
- 🧠 Re-usable training pipeline with data cleaning + scaling
- ⚙️ FastAPI inference service with health + metrics endpoints
- 📦 Dockerized deployment + typed Pydantic schemas
- ✅ Pytest coverage for service logic

## Project structure
```
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   └── service.py
├── data/
│   └── mock_iot_logs.csv
├── models/              # Saved scaler + model (created after training)
├── tests/
│   └── test_prediction.py
├── training/
│   └── train_model.py
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

## Dataset
`data/mock_iot_logs.csv` contains synthetic telemetry with the required schema:

| column        | type   | example               |
|---------------|--------|-----------------------|
| id            | int    | 1                     |
| timestamp     | ISO    | 2025-11-26T08:00:00Z  |
| equipment_id  | str    | MRI-01                |
| temperature   | float  | 65.2                  |
| pressure      | float  | 1.8                   |
| vibration     | float  | 0.02 (optional)       |
| status        | str    | normal / failure      |

Training focuses on `status != "failure"` rows to learn “normal” behaviour.

## Setup
### 1. Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Install dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## Train the model
```powershell
python training/train_model.py
```
- Cleans the CSV (drops NaNs, sorts, filters failures)
- Fits `StandardScaler` + `IsolationForest`
- Saves artifacts to `models/scaler.joblib` and `models/isolation_forest.joblib`

## Run tests
```powershell
pytest
```

## Start the FastAPI service
```powershell
uvicorn app.main:app --reload --port 8000
```

### Sample requests
Health check:
```bash
curl http://localhost:8000/health
```

Prediction:
```bash
curl -X POST http://localhost:8000/predict \
		-H "Content-Type: application/json" \
		-d '{
					"equipment_id": "MRI-01",
					"temperature": 72.1,
					"pressure": 2.1,
					"vibration": 0.05
				}'
```
Response:
```json
{
	"equipment_id": "MRI-01",
	"anomaly_score": 0.82,
	"is_failure_risk": true,
	"maintenance_warning": "High risk: schedule immediate inspection",
	"generated_at": "2025-11-27T10:15:00Z"
}
```

Metrics:
```bash
curl http://localhost:8000/metrics/basic
```

## Docker
```bash
docker build -t equipment-agent .
docker run -p 8000:8000 equipment-agent
```

## Environment vars & config
Configuration (paths, thresholds) lives in `app/config.py`. Update `anomaly_threshold` if you need a stricter or looser warning trigger.

---
Clone, train, run, and start predicting equipment failures in minutes 🚑⚙️
