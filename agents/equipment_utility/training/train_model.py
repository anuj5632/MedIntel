from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Tuple

import joblib
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "mock_iot_logs.csv"
MODEL_DIR = BASE_DIR / "models"
SCALER_PATH = MODEL_DIR / "scaler.joblib"
MODEL_PATH = MODEL_DIR / "isolation_forest.joblib"
CALIBRATION_PATH = MODEL_DIR / "calibration.json"
FEATURES = ["temperature", "pressure", "vibration"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Data file not found at {path}")
    logger.info("Loading data from %s", path)
    return pd.read_csv(path, parse_dates=["timestamp"])


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning %d rows", len(df))
    df = df.dropna(subset=["temperature", "pressure"])
    df = df.sort_values("timestamp")
    if "status" in df.columns:
        df = df[df["status"].str.lower() != "failure"]
    df["vibration"] = df["vibration"].fillna(df["vibration"].median())
    return df


def train(df: pd.DataFrame) -> Tuple[StandardScaler, IsolationForest, dict[str, float]]:
    if df.empty:
        raise ValueError("No training data after preprocessing")
    scaler = StandardScaler()
    features = df[FEATURES].values
    logger.info("Fitting scaler on shape %s", features.shape)
    scaled = scaler.fit_transform(features)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
    )
    logger.info("Training IsolationForest...")
    model.fit(scaled)

    calibration = build_calibration_metadata(model, scaled)
    return scaler, model, calibration


def build_calibration_metadata(model: IsolationForest, scaled_features: np.ndarray) -> dict[str, float]:
    raw_scores = -model.score_samples(scaled_features)
    return {
        "score_min": float(np.min(raw_scores)),
        "score_max": float(np.max(raw_scores)),
        "score_mean": float(np.mean(raw_scores)),
        "score_std": float(np.std(raw_scores) + 1e-9),
    }


def save_artifacts(
    scaler: StandardScaler,
    model: IsolationForest,
    calibration: dict[str, float],
) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(model, MODEL_PATH)
    with CALIBRATION_PATH.open("w", encoding="utf-8") as fh:
        json.dump(calibration, fh)
    logger.info("Saved scaler to %s", SCALER_PATH)
    logger.info("Saved model to %s", MODEL_PATH)
    logger.info("Saved calibration metadata to %s", CALIBRATION_PATH)


def main(data_path: Path = DATA_PATH) -> None:
    df = load_data(data_path)
    df_clean = preprocess(df)
    scaler, model, calibration = train(df_clean)
    save_artifacts(scaler, model, calibration)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Equipment & Utility Agent model")
    parser.add_argument(
        "--data-path",
        type=Path,
        default=DATA_PATH,
        help="Path to CSV containing IoT logs",
    )
    args = parser.parse_args()
    main(args.data_path)
