"""
Dataset Generator for Hospital Daily Load Forecasting
Generates synthetic time-series data with realistic hospital admission patterns.
"""


# Configuration


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "hospital_daily_load.csv")

NUM_DAYS = random.randint(365, 1825)
START_DATE = datetime(2022, 1, 1)
HOSPITAL_IDS = [f"HOSP_{i+1}" for i in range(5)]

festival_gap = random.randint(20, 40)
festival_days = set()
day = 0
while day < NUM_DAYS:
    festival_days.add(day)
    day += festival_gap + random.randint(-3, 3)

flu_season_months = {10, 11, 12, 1, 2}

os.makedirs(DATA_DIR, exist_ok=True)

rows = []
for day in range(NUM_DAYS):
    date = START_DATE + timedelta(days=day)
    dow = date.weekday()
    month = date.month
    is_flu_season = month in flu_season_months
    is_festival = day in festival_days
    pollution_index = np.random.normal(120, 40)
    if random.random() < 0.05:
        pollution_index = np.random.randint(250, 400)
    for hosp in HOSPITAL_IDS:
        base = 80 + 10 * dow + 5 * (month == 1) + 8 * (month == 12)
        admissions = base
        if is_festival:
            admissions += np.random.randint(30, 80)
        if is_flu_season:
            admissions += np.random.randint(20, 60)
        if pollution_index > 250:
            admissions += np.random.randint(10, 40)
        admissions += np.random.normal(0, 10)
        admissions = max(0, int(admissions))
        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "hospital_id": hosp,
            "admissions": admissions,
            "pollution_index": int(pollution_index),
            "is_festival": int(is_festival),
            "is_flu_season": int(is_flu_season)
        })
df = pd.DataFrame(rows)
df.to_csv(DATA_PATH, index=False)
print(f"Dataset generated: {DATA_PATH} ({len(df)} rows)")
