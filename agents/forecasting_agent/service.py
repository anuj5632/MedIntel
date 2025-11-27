"""
FastAPI Service for Hospital Demand Forecasting
Provides REST API endpoints for real-time predictions and resource recommendations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
import joblib
import numpy as np
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(__file__)
MODEL_FILE = os.path.join(BASE_DIR, 'models', 'demand_model.joblib')
FEATURE_COLS_FILE = os.path.join(BASE_DIR, 'models', 'feature_cols.joblib')

# Initialize FastAPI app
app = FastAPI(
    title="MedIntel Forecasting Agent",
    description="Time-series forecasting system for hospital demand prediction",
    version="1.0.0"
)

# Global model and feature columns
model = None
feature_cols = None

# ============== PYDANTIC MODELS ==============

class ForecastRequest(BaseModel):
    """Request schema for forecast endpoint."""
    hospital_id: str = Field(..., example="HOSP_001", description="Hospital identifier")
    start_date: str = Field(..., example="2025-12-01", description="Start date (YYYY-MM-DD)")
    horizon_days: int = Field(default=15, ge=1, le=90, description="Number of days to forecast")
    pollution_index: float = Field(default=120, ge=0, le=500, description="Air Quality Index")
    is_festival: bool = Field(default=False, description="Is festival period")
    is_flu_season: bool = Field(default=False, description="Is flu season")

class PredictionRecord(BaseModel):
    """Single day prediction."""
    date: str
    predicted_admissions: float
    risk_level: str
    extra_beds: int
    extra_doctors: int
    extra_nurses: int

class ForecastResponse(BaseModel):
    """Response schema for forecast endpoint."""
    hospital_id: str
    forecast_date: str
    predictions: List[PredictionRecord]
    peak_day: str
    peak_load: float
    summary: Dict

# ============== HELPER FUNCTIONS ==============

def load_model():
    """Load pre-trained model and feature columns."""
    global model, feature_cols
    
    if not os.path.exists(MODEL_FILE):
        logger.error(f"Model file not found: {MODEL_FILE}")
        raise RuntimeError(f"Model not found. Please train model first.")
    
    if not os.path.exists(FEATURE_COLS_FILE):
        logger.error(f"Feature columns file not found: {FEATURE_COLS_FILE}")
        raise RuntimeError(f"Feature columns file not found.")
    
    model = joblib.load(MODEL_FILE)
    feature_cols = joblib.load(FEATURE_COLS_FILE)
    
    logger.info(f"✓ Model loaded successfully from {MODEL_FILE}")
    logger.info(f"✓ Features: {feature_cols}")

def get_risk_level(admissions: float) -> str:
    """Determine risk level based on admission count."""
    if admissions < 100:
        return "LOW"
    elif admissions < 200:
        return "MEDIUM"
    else:
        return "HIGH"

def calculate_resources(admissions: float) -> tuple:
    """
    Calculate required resources based on predicted admissions.
    
    Logic:
    - Every 20 patients above 100 baseline:
      +2 beds, +1 doctor, +2 nurses
    """
    baseline = 100
    
    if admissions <= baseline:
        return (2, 1, 2)  # Minimum staff
    
    excess = admissions - baseline
    extra_beds = int((excess / 20) * 2)
    extra_doctors = int((excess / 20) * 1)
    extra_nurses = int((excess / 20) * 2)
    
    return (extra_beds, extra_doctors, extra_nurses)

def create_features(date: datetime, pollution_index: float, is_festival: bool, 
                   is_flu_season: bool, lag_1: float, lag_7: float, lag_30: float,
                   rolling_7_mean: float, rolling_7_std: float, rolling_30_mean: float) -> dict:
    """Create feature dictionary for prediction."""
    day_of_week = date.weekday()
    month = date.month
    day_of_month = date.day
    quarter = (month - 1) // 3 + 1
    
    features = {
        'day_of_week': day_of_week,
        'month': month,
        'day_of_month': day_of_month,
        'quarter': quarter,
        'pollution_index': pollution_index,
        'is_festival': int(is_festival),
        'is_flu_season': int(is_flu_season),
        'lag_1': lag_1,
        'lag_7': lag_7,
        'lag_30': lag_30,
        'rolling_7_mean': rolling_7_mean,
        'rolling_7_std': rolling_7_std,
        'rolling_30_mean': rolling_30_mean
    }
    
    return features

def build_feature_vector(features_dict: dict) -> np.ndarray:
    """Build feature vector in correct order for model prediction."""
    return np.array([[features_dict[col] for col in feature_cols]])

# ============== API ENDPOINTS ==============

@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    try:
        load_model()
        logger.info("✓ FastAPI server started successfully")
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return {
        "service": "MedIntel Forecasting Agent",
        "version": "1.0.0",
        "status": "online",
        "model_loaded": model is not None
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_available": model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/forecast", response_model=ForecastResponse, tags=["Forecasting"])
async def forecast(request: ForecastRequest):
    """
    Generate hospital demand forecast.
    
    Returns:
    - Daily admission predictions
    - Risk levels
    - Resource requirements (beds, doctors, nurses)
    - Peak day and load
    """
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Service unavailable.")
    
    try:
        # Parse start date
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        
        # Ensure horizon is native int to avoid numpy types
        horizon = int(request.horizon_days)

        # Initialize time-series values (using baseline estimates)
        current_admissions = 85.0  # Baseline
        lag_1 = current_admissions
        lag_7 = current_admissions
        lag_30 = current_admissions
        rolling_7_mean = current_admissions
        rolling_7_std = 5.0
        rolling_30_mean = current_admissions
        
        predictions = []
        all_predictions = []
        
        # Generate forecast for each day
        for day_offset in range(horizon):
            # Ensure day_offset is a built-in int (avoid numpy types from JSON parsing)
            day_offset_int = int(day_offset)
            forecast_date = start_date + timedelta(days=day_offset_int)
            
            # Create features for this day
            features_dict = create_features(
                date=forecast_date,
                pollution_index=request.pollution_index,
                is_festival=request.is_festival,
                is_flu_season=request.is_flu_season,
                lag_1=lag_1,
                lag_7=lag_7,
                lag_30=lag_30,
                rolling_7_mean=rolling_7_mean,
                rolling_7_std=rolling_7_std,
                rolling_30_mean=rolling_30_mean
            )
            
            # Build feature vector and predict
            X_pred = build_feature_vector(features_dict)
            predicted_admissions = float(model.predict(X_pred)[0])
            predicted_admissions = max(40, predicted_admissions)  # Minimum threshold
            
            # Determine risk level
            risk_level = get_risk_level(predicted_admissions)
            
            # Calculate resources
            extra_beds, extra_doctors, extra_nurses = calculate_resources(predicted_admissions)
            
            # Create prediction record
            prediction = PredictionRecord(
                date=forecast_date.strftime("%Y-%m-%d"),
                predicted_admissions=round(predicted_admissions, 2),
                risk_level=risk_level,
                extra_beds=extra_beds,
                extra_doctors=extra_doctors,
                extra_nurses=extra_nurses
            )
            
            predictions.append(prediction)
            all_predictions.append(predicted_admissions)
            
            # Update lag and rolling values for next iteration
            lag_30 = lag_7
            lag_7 = lag_1
            lag_1 = predicted_admissions
            rolling_30_mean = np.mean(all_predictions[-30:] if len(all_predictions) >= 30 else all_predictions)
            rolling_7_mean = np.mean(all_predictions[-7:] if len(all_predictions) >= 7 else all_predictions)
            rolling_7_std = np.std(all_predictions[-7:] if len(all_predictions) >= 7 else [predicted_admissions])
        
        # Find peak day and load (ensure native Python int for timedelta)
        peak_idx = int(np.argmax(all_predictions))
        peak_day = (start_date + timedelta(days=peak_idx)).strftime("%Y-%m-%d")
        peak_load = round(float(all_predictions[peak_idx]), 2)
        
        # Summary statistics
        summary = {
            "avg_daily_admissions": round(np.mean(all_predictions), 2),
            "min_daily_admissions": round(float(np.min(all_predictions)), 2),
            "max_daily_admissions": round(float(np.max(all_predictions)), 2),
            "total_admissions_period": round(float(np.sum(all_predictions)), 2),
            "high_risk_days": sum(1 for p in all_predictions if p >= 200),
            "medium_risk_days": sum(1 for p in all_predictions if 100 <= p < 200),
            "low_risk_days": sum(1 for p in all_predictions if p < 100)
        }
        
        return ForecastResponse(
            hospital_id=request.hospital_id,
            forecast_date=datetime.now().isoformat(),
            predictions=predictions,
            peak_day=peak_day,
            peak_load=peak_load,
            summary=summary
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request data: {str(e)}")
    except Exception as e:
        logger.error(f"Forecast error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")

@app.get("/info", tags=["Information"])
async def model_info():
    """Get information about the loaded model."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": type(model).__name__,
        "model_file": MODEL_FILE,
        "features_used": feature_cols,
        "num_features": len(feature_cols),
        "model_parameters": {
            "n_estimators": model.n_estimators,
            "max_depth": model.max_depth,
            "min_samples_split": model.min_samples_split
        }
    }

@app.get("/docs", tags=["Documentation"])
async def documentation():
    """API documentation endpoint."""
    return {
        "title": "MedIntel Forecasting Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /forecast": "Generate hospital demand forecast",
            "GET /health": "Check service health",
            "GET /info": "Get model information",
            "GET /docs": "API documentation (auto-generated at /docs)"
        },
        "example_request": {
            "hospital_id": "HOSP_001",
            "start_date": "2025-12-01",
            "horizon_days": 15,
            "pollution_index": 120,
            "is_festival": False,
            "is_flu_season": False
        }
    }

# ============== ERROR HANDLERS ==============

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all exceptions."""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001, reload=True)
