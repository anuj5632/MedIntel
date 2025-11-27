import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class MedicalSupplyInventoryAgent:
    def __init__(self, forecast_horizon=7):
        self.forecast_horizon = forecast_horizon
        self.model = None
        self.trained_items = None

    def _build_features(self, df):
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["item_id", "date"])
        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month
        df["lag_1"] = df.groupby("item_id")["qty_used"].shift(1)
        df["lag_7"] = df.groupby("item_id")["qty_used"].shift(7)
        df["roll_7_mean"] = df.groupby("item_id")["qty_used"].shift(1).rolling(7).mean()
        df = df.dropna()
        return df

    def fit(self, usage_logs):
        df = self._build_features(usage_logs)
        X = df[["item_id", "lag_1", "lag_7", "roll_7_mean", "day_of_week", "month"]]
        y = df["qty_used"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore"), ["item_id"]),
                ("num", "passthrough", ["lag_1", "lag_7", "roll_7_mean", "day_of_week", "month"]),
            ]
        )
        model = XGBRegressor(objective="reg:squarederror", n_estimators=300, max_depth=6, learning_rate=0.05)
        pipeline = Pipeline([("preprocess", preprocessor), ("model", model)])
        pipeline.fit(X, y)
        self.model = pipeline
        self.trained_items = usage_logs["item_id"].unique().tolist()

    def forecast_item(self, usage_logs, item_id):
        df = usage_logs[usage_logs["item_id"] == item_id].copy()
        df = df.sort_values("date")
        last_vals = df["qty_used"].values[-7:]
        preds = []
        current_vals = list(last_vals)
        current_date = pd.to_datetime(df["date"].max())
        for i in range(self.forecast_horizon):
            d = current_date + pd.Timedelta(days=i+1)
            feat = {
                "item_id": item_id,
                "lag_1": current_vals[-1],
                "lag_7": current_vals[-7],
                "roll_7_mean": np.mean(current_vals[-7:]),
                "day_of_week": d.dayofweek,
                "month": d.month
            }
            X = pd.DataFrame([feat])
            y_pred = float(self.model.predict(X)[0])
            preds.append({"date": d, "item_id": item_id, "forecast_qty": max(y_pred, 0)})
            current_vals.append(y_pred)
        return pd.DataFrame(preds)

    def forecast_all(self, usage_logs):
        out = []
        for item in self.trained_items:
            out.append(self.forecast_item(usage_logs, item))
        return pd.concat(out, ignore_index=True)

    def generate_reorder_alerts(self, forecasts, current_stock, lead_times):
        alerts = []
        for item, stock in current_stock.items():
            fc = forecasts[forecasts["item_id"] == item].sort_values("date")
            lead = lead_times.get(item, 7)
            window = fc.head(lead)
            mean_d = window["forecast_qty"].mean()
            reorder_point = mean_d * lead
            if stock <= reorder_point:
                alerts.append({
                    "item_id": item,
                    "current_stock": stock,
                    "reorder_point": float(reorder_point),
                    "suggested_order_qty": int(reorder_point - stock + reorder_point*0.2)
                })
        return alerts

dates = pd.date_range(start="2024-01-01", periods=120)

qty = np.concatenate([
    np.random.poisson(lam=30, size=len(dates)),
    np.random.poisson(lam=20, size=len(dates)),
    np.random.poisson(lam=50, size=len(dates))
])

usage_logs = pd.DataFrame({
    "date": np.repeat(dates, 3),
    "item_id": ["gloves", "syringe", "saline"] * len(dates),
    "qty_used": qty
})

current_stock = {"gloves": 120, "syringe": 80, "saline": 160}
lead_times = {"gloves": 5, "syringe": 7, "saline": 4}

agent = MedicalSupplyInventoryAgent()
agent.fit(usage_logs)

forecasts = agent.forecast_all(usage_logs)
alerts = agent.generate_reorder_alerts(forecasts, current_stock, lead_times)
print("Usage logs:\n", usage_logs.head(15))
print("FORECASTS:\n", forecasts.head(15))
print("\nALERTS:\n", alerts)
