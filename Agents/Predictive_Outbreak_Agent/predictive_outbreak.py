import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy.signal import find_peaks

# Prophet import (works for both 'prophet' and older 'fbprophet')
try:
    from prophet import Prophet
except ImportError:
    from fbprophet import Prophet


class PredictiveOutbreakAgent:
    """
    Predictive Outbreak Agent

    - Input: DataFrame with columns ['date', 'cases'] and optional ['aqi']
    - Output: dict with outbreak risk index (0-5) + explanation + series for plotting
    """

    def __init__(self, forecast_horizon: int = 7, window_days: int = 7, n_clusters: int = 3):
        self.forecast_horizon = forecast_horizon
        self.window_days = window_days
        self.n_clusters = n_clusters

    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # Aggregate to daily level (useful if multiple hospitals/rows per day)
        agg = {"cases": "sum"}
        if "aqi" in df.columns:
            agg["aqi"] = "mean"
        df_daily = df.groupby("date", as_index=False).agg(agg)

        return df_daily

    def _fit_prophet(self, df_daily: pd.DataFrame):
        df_prophet = df_daily[["date", "cases"]].rename(columns={"date": "ds", "cases": "y"})
        m = Prophet(daily_seasonality=True, weekly_seasonality=True)
        m.fit(df_prophet)

        future = m.make_future_dataframe(periods=self.forecast_horizon)
        forecast = m.predict(future)

        # merge baseline back to original daily data
        merged = df_daily.merge(
            forecast[["ds", "yhat"]],
            left_on="date",
            right_on="ds",
            how="left"
        )
        merged["baseline"] = merged["yhat"]
        merged["residual"] = merged["cases"] - merged["baseline"]

        return m, forecast, merged

    def _build_feature_matrix(self, merged: pd.DataFrame) -> pd.DataFrame:
        """
        Build features over rolling windows for clustering:
        - growth rate over window
        - mean residual
        - max residual
        - last day's AQI (if available)
        """
        df = merged.copy()
        df = df.reset_index(drop=True)

        feats = []
        n = len(df)
        W = self.window_days

        for end_idx in range(W, n):
            win = df.iloc[end_idx - W:end_idx]
            start_cases = win["cases"].iloc[0]
            end_cases = win["cases"].iloc[-1]

            growth = (end_cases - start_cases) / (start_cases + 1e-3)  # avoid /0
            mean_resid = win["residual"].mean()
            max_resid = win["residual"].max()

            if "aqi" in df.columns:
                last_aqi = win["aqi"].iloc[-1]
            else:
                last_aqi = 0.0

            feats.append({
                "end_date": win["date"].iloc[-1],
                "growth": growth,
                "mean_residual": mean_resid,
                "max_residual": max_resid,
                "last_aqi": last_aqi
            })

        feat_df = pd.DataFrame(feats)
        return feat_df

    def _cluster_risk(self, feat_df: pd.DataFrame):
        """
        Fit KMeans on the feature history to learn "low / medium / high" risk patterns.
        Then map latest point to a cluster and risk score (0-5).
        """
        if len(feat_df) < self.n_clusters:
            # Not enough history for clustering, fallback later in risk calculation
            return None, None, None

        X = feat_df[["growth", "mean_residual", "max_residual", "last_aqi"]].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        feat_df["cluster"] = kmeans.fit_predict(X_scaled)

        # compute a severity score per cluster center
        centers = kmeans.cluster_centers_
        # undo scaling only for interpretability if needed (not strictly required)
        # severity heuristic: high growth + high residuals + high aqi = higher severity
        severity_scores = {}
        for i in range(self.n_clusters):
            g, mr, mxr, aqi = centers[i]
            # they are in standardized space, but relative comparison is ok
            severity = g + mr + mxr + 0.5 * aqi
            severity_scores[i] = severity

        # normalize severity to 0..1
        sev_vals = np.array(list(severity_scores.values()))
        sev_min, sev_max = sev_vals.min(), sev_vals.max()
        norm_scores = {}
        for k, v in severity_scores.items():
            if sev_max == sev_min:
                norm = 0.0
            else:
                norm = (v - sev_min) / (sev_max - sev_min)
            norm_scores[k] = norm

        # latest point
        latest_row = feat_df.iloc[-1]
        latest_cluster = int(latest_row["cluster"])
        latest_severity_norm = norm_scores[latest_cluster]

        # map to base risk index (0-4)
        base_risk = int(round(latest_severity_norm * 4))

        return base_risk, latest_cluster, latest_row

    def _detect_spikes(self, merged: pd.DataFrame, lookback_days: int = 14):
        """
        Use scipy.signal.find_peaks on residuals to detect recent spikes.
        Return indices of peaks and whether there's a recent spike.
        """
        resid = merged["residual"].values
        # use a simple prominence threshold: 1 std of residuals
        if len(resid) < 5:
            return [], False

        prom = np.nanstd(resid)
        if prom == 0 or np.isnan(prom):
            prom = 1.0

        peaks, _ = find_peaks(resid, prominence=prom)
        peaks = peaks.tolist()

        # check if there is a peak in the last lookback_days
        if len(merged) > 0:
            last_idx = len(merged) - 1
            cutoff_idx = max(0, last_idx - lookback_days)
            recent_spike = any(p >= cutoff_idx for p in peaks)
        else:
            recent_spike = False

        return peaks, recent_spike

    def compute_outbreak_risk(self, df_raw: pd.DataFrame) -> dict:
        """
        Main public method:
        df_raw: DataFrame with ['date', 'cases'] and optional ['aqi']
        returns: dict with risk_index (0-5) and explanation.
        """
        df_daily = self._prepare_data(df_raw)
        if len(df_daily) < 14:
            return {
                "risk_index": 0,
                "risk_level": "Insufficient data",
                "reason": "Need at least 14 days of data to estimate outbreak risk.",
                "latest_metrics": {},
                "time_series": {}
            }

        model, forecast, merged = self._fit_prophet(df_daily)
        feat_df = self._build_feature_matrix(merged)
        base_risk, cluster_label, latest_feat = self._cluster_risk(feat_df)

        # Fallback if clustering not possible
        if base_risk is None:
            base_risk = 0
            cluster_label = -1
            latest_feat = feat_df.iloc[-1] if len(feat_df) else None

        peaks_idx, recent_spike = self._detect_spikes(merged)

        # compute residual zscore for latest day
        latest_row = merged.iloc[-1]
        resid_series = merged["residual"].values
        resid_mean = np.nanmean(resid_series)
        resid_std = np.nanstd(resid_series) if np.nanstd(resid_series) > 0 else 1.0
        resid_z = (latest_row["residual"] - resid_mean) / resid_std

        # risk bonus for recent spike and high residual
        bonus = 0
        if recent_spike:
            bonus += 1
        if resid_z > 1.5:
            bonus += 1
        if "aqi" in df_daily.columns and df_daily["aqi"].iloc[-1] > 200:
            bonus += 1

        risk_index = int(np.clip(base_risk + bonus, 0, 5))

        # human-readable level
        levels = ["Minimal", "Low", "Guarded", "Elevated", "High", "Severe"]
        risk_level = levels[risk_index]

        latest_metrics = {
            "date": latest_row["date"].strftime("%Y-%m-%d"),
            "cases": int(latest_row["cases"]),
            "aqi": float(latest_row["aqi"]) if "aqi" in latest_row else None,
            "growth_7d": float(latest_feat["growth"]) if latest_feat is not None else None,
            "residual_zscore": float(resid_z),
            "recent_peak": bool(recent_spike)
        }

        # explanation string
        reason_parts = []
        if risk_index <= 1:
            reason_parts.append("Stable or low case growth.")
        else:
            if latest_feat is not None and latest_feat["growth"] > 0.3:
                reason_parts.append("Significant upward trend in cases.")
            if resid_z > 1.5:
                reason_parts.append("Cases are well above the expected baseline.")
            if recent_spike:
                reason_parts.append("Recent spike detected in residuals.")
            if latest_metrics["aqi"] and latest_metrics["aqi"] > 200:
                reason_parts.append("Poor air quality may be contributing to respiratory cases.")
        if not reason_parts:
            reason_parts.append("No strong outbreak signals detected.")

        reason = " ".join(reason_parts)

        # Export time-series for charts
        time_series = {
            "dates": merged["date"].dt.strftime("%Y-%m-%d").tolist(),
            "cases": merged["cases"].astype(float).tolist(),
            "baseline": merged["baseline"].astype(float).tolist(),
            "residuals": merged["residual"].astype(float).tolist(),
            "peaks_idx": peaks_idx
        }

        return {
            "risk_index": risk_index,
            "risk_level": risk_level,
            "cluster_label": int(cluster_label),
            "reason": reason,
            "latest_metrics": latest_metrics,
            "time_series": time_series
        }


# -------------------------
# Quick local demo (optional)
# -------------------------
if __name__ == "__main__":
    # simulate 60 days data with a fake outbreak
    rng = pd.date_range("2025-08-01", periods=60, freq="D")
    base = 50 + np.sin(np.arange(60) / 6) * 5
    noise = np.random.normal(0, 5, size=60)

    # inject a surge in last 10 days
    surge = np.array([0]*50 + [i*4 for i in range(10)])
    cases = np.maximum(0, base + noise + surge).astype(int)

    aqi = 120 + np.random.normal(0, 15, size=60)  # mild pollution

    df_demo = pd.DataFrame({
        "date": rng,
        "cases": cases,
        "aqi": aqi
    })

    agent = PredictiveOutbreakAgent()
    result = agent.compute_outbreak_risk(df_demo)
    print(result)
