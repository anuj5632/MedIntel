"""
Model Training Script for Hospital Demand Forecasting
Trains a RandomForestRegressor with engineered time-series features.
"""


import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib


BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "data", "hospital_daily_load.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_FILE = os.path.join(MODEL_DIR, "demand_model.joblib")
FEATURE_COLS_FILE = os.path.join(MODEL_DIR, "feature_cols.joblib")


def feature_engineering(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["hospital_id", "date"]).reset_index(drop=True)
    df["day_of_week"] = df["date"].dt.weekday
    df["month"] = df["date"].dt.month
    df["day_of_month"] = df["date"].dt.day
    df["lag_1"] = df.groupby("hospital_id")["admissions"].shift(1)
    df["lag_7"] = df.groupby("hospital_id")["admissions"].shift(7)
    df["rolling_7"] = df.groupby("hospital_id")["admissions"].rolling(7).mean().reset_index(0, drop=True)
    df = df.fillna(0)
    return df


def main():
    print("Starting training pipeline...")
    if not os.path.exists(DATA_FILE):
        print(f"Dataset not found: {DATA_FILE}. Run generate_dataset.py first.")
        return

    df = pd.read_csv(DATA_FILE)
    df = feature_engineering(df)

    features = [
        "day_of_week", "month", "day_of_month", "lag_1", "lag_7", "rolling_7",
        "pollution_index", "is_festival", "is_flu_season"
    ]

    X = df[features]
    y = df["admissions"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    print(f"Model trained. MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.4f}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    joblib.dump(features, FEATURE_COLS_FILE)
    print(f"Model saved to {MODEL_FILE}")
    print(f"Feature columns saved to {FEATURE_COLS_FILE}")


if __name__ == "__main__":
    main()
def load_and_prepare_data():
    """
    Load CSV and perform initial data preparation.
    """
    print("Loading dataset...")
    
    if not os.path.exists(DATA_FILE):
        print(f"✗ Error: Dataset not found at {DATA_FILE}")
        print("  Please run: python generate_dataset.py")
        sys.exit(1)
    
    df = pd.read_csv(DATA_FILE)
    
    # Convert date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by hospital and date
    df = df.sort_values(['hospital_id', 'date']).reset_index(drop=True)
    
    print(f"✓ Loaded {len(df)} records from {df['date'].min()} to {df['date'].max()}")
    return df

def engineer_features(df):
    """
    Create lag and rolling window features for time-series prediction.
    """
    print("Engineering features...")
    
    df = df.copy()
    
    # Date-based features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    df['quarter'] = df['date'].dt.quarter
    
    # Create lag features (for each hospital separately)
    df_with_lags = []
    
    for hospital in df['hospital_id'].unique():
        hospital_data = df[df['hospital_id'] == hospital].copy()
        
        # Lag features (previous days' admissions)
        hospital_data['lag_1'] = hospital_data['admissions'].shift(1)
        hospital_data['lag_7'] = hospital_data['admissions'].shift(7)
        hospital_data['lag_30'] = hospital_data['admissions'].shift(30)
        
        # Rolling window features
        hospital_data['rolling_7_mean'] = hospital_data['admissions'].rolling(window=7, min_periods=1).mean()
        hospital_data['rolling_7_std'] = hospital_data['admissions'].rolling(window=7, min_periods=1).std()
        hospital_data['rolling_30_mean'] = hospital_data['admissions'].rolling(window=30, min_periods=1).mean()
        
        df_with_lags.append(hospital_data)
    
    df = pd.concat(df_with_lags, ignore_index=True)
    df = df.sort_values(['hospital_id', 'date']).reset_index(drop=True)
    
    # Fill NaN values from lags (first rows)
    df = df.fillna(df['admissions'].mean())
    
    print(f"✓ Created features: {[col for col in df.columns if col not in ['date', 'hospital_id', 'admissions']]}")
    return df

def prepare_training_data(df):
    """
    Prepare features and target for model training.
    """
    print("Preparing training data...")
    
    # Feature columns (exclude target and identifiers)
    feature_cols = [
        'day_of_week', 'month', 'day_of_month', 'quarter',
        'pollution_index', 'is_festival', 'is_flu_season',
        'lag_1', 'lag_7', 'lag_30',
        'rolling_7_mean', 'rolling_7_std', 'rolling_30_mean'
    ]
    
    X = df[feature_cols].values
    y = df['admissions'].values
    
    print(f"✓ Feature matrix shape: {X.shape}")
    print(f"✓ Target shape: {y.shape}")
    print(f"✓ Features: {feature_cols}")
    
    return X, y, feature_cols

def train_model(X, y, feature_cols):
    """
    Train RandomForestRegressor model.
    """
    print("\nTraining Random Forest model...")
    
    # Split data (temporal split is ideal, but we'll use random for now)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    test_r2 = r2_score(y_test, y_pred_test)
    
    print(f"\n✓ Model trained successfully!")
    print(f"✓ Training MAE: {train_mae:.2f}")
    print(f"✓ Testing MAE: {test_mae:.2f}")
    print(f"✓ Testing RMSE: {test_rmse:.2f}")
    print(f"✓ Testing R²: {test_r2:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n✓ Top 5 important features:")
    print(feature_importance.head())
    
    return model

def save_model(model, feature_cols):
    """
    Save trained model and feature information.
    """
    print("\nSaving model...")
    
    os.makedirs(os.path.dirname(MODEL_FILE), exist_ok=True)
    
    # Save model
    joblib.dump(model, MODEL_FILE)
    print(f"✓ Model saved to: {MODEL_FILE}")
    
    # Save feature columns for later use
    joblib.dump(feature_cols, os.path.join(os.path.dirname(MODEL_FILE), 'feature_cols.joblib'))
    print(f"✓ Feature columns saved")

def main():
    """
    Main training pipeline.
    """
    print("=" * 60)
    print("HOSPITAL DEMAND FORECASTING MODEL TRAINER")
    print("=" * 60)
    
    # Load and prepare
    df = load_and_prepare_data()
    df = engineer_features(df)
    X, y, feature_cols = prepare_training_data(df)
    
    # Train
    model = train_model(X, y, feature_cols)
    
    # Save
    save_model(model, feature_cols)
    
    print("\n" + "=" * 60)
    print("✓ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Model ready for forecasting at: {MODEL_FILE}")

if __name__ == '__main__':
    main()
