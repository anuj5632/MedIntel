# MedIntel Agents (Agents Branch)# MedIntel Agents# Equipment & Utility Agent (Agent 4)



This branch aggregates several intelligent assistants that power MedIntel operations. Most agents live under the lowercase `agents/` directory; a few legacy scripts remain in `Agents/` (uppercase).



| Agent | Path | Highlights |This branch aggregates multiple intelligent assistants that power MedIntel operations. Each agent lives in its own folder under `Agents/`:Predictive maintenance service for hospital equipment. It ingests IoT-style sensor readings, detects anomalies with Isolation Forest, and surfaces JSON maintenance warnings through a FastAPI service.

| --- | --- | --- |

| Forecasting Agent | `agents/forecasting_agent/` | Demand forecasting service with dataset generators and notebooks. |

| Staff Optimization Agent | `agents/staff_optimization/` | Scheduling heuristics and staffing utilities. |

| Inventory Management Agent | `Agents/InventoryManagement/` | Legacy medical supply monitoring scripts (kept for compatibility). || Agent | Path | Highlights |## Features

| **Equipment & Utility Agent (Agent 4)** | `agents/equipment_utility/` | FastAPI anomaly-detection microservice with training pipeline, data, Dockerfile, and tests. |

| --- | --- | --- |- 📈 Isolation Forest anomaly detection on temperature, pressure, and vibration signals

## Working on the Equipment & Utility Agent

| Forecasting Agent | `Agents/forecasting_agent/` | Demand forecasting notebooks, dataset generators, and inference service. |- 🧠 Re-usable training pipeline with data cleaning + scaling

```powershell

cd agents/equipment_utility| Staff Optimization Agent | `Agents/staff_optimization/` | Scheduling heuristics / optimization utilities. |- ⚙️ FastAPI inference service with health + metrics endpoints

python -m venv .venv

.\.venv\Scripts\activate| Inventory Management Agent | `Agents/InventoryManagement/` | Scripts for hospital supply monitoring. |- 📦 Dockerized deployment + typed Pydantic schemas

pip install -r requirements.txt

python training/train_model.py| **Equipment & Utility Agent** | `Agents/equipment_utility/` | FastAPI anomaly-detection service for predictive maintenance (Agent 4). |- ✅ Pytest coverage for service logic

uvicorn app.main:app --host 0.0.0.0 --port 8000

```



That folder also includes `scripts/run_service_check.py` for smoke tests, pytest coverage in `tests/`, saved models under `models/`, and its own detailed README. To add future agents, create another folder under `agents/`, document it with a README, and list it inside `agents/__init__.py` so it is easy to discover.To work on a specific agent, `cd` into that directory and follow its local README. For example, the new Equipment & Utility Agent includes its own training data, FastAPI app, Dockerfile, smoke-test script, and README under `Agents/equipment_utility/`.## Project structure


```

```powershell.

cd Agents/equipment_utility├── app/

python -m venv .venv│   ├── __init__.py

.\.venv\Scripts\activate│   ├── config.py

pip install -r requirements.txt│   ├── main.py

python training/train_model.py│   ├── models.py

uvicorn app.main:app --host 0.0.0.0 --port 8000│   └── service.py

```├── data/

│   └── mock_iot_logs.csv

Feel free to add additional agents by creating a new folder inside `Agents/`, documenting it with a README, and wiring it into `Agents/__init__.py` for discoverability.├── models/              # Saved scaler + model (created after training)

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
