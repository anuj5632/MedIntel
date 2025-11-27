# staff_agent.py

from dataclasses import dataclass
from typing import List, Dict, Any
import math

# -----------------------------
# Data model
# -----------------------------
@dataclass
class Staff:
    id: str
    role: str
    max_hours_per_day: int
    cost_per_hour: float


# -----------------------------
# Core Agent Logic
# -----------------------------
def optimize_staff_schedule(demand: List[int], staff_list: List[Staff]) -> Dict[str, Any]:
    """
    Simple but powerful staff scheduling agent.

    Input:
      - demand: list[int] -> required staff per hour (e.g. length 24 for 24 hours)
      - staff_list: list[Staff]

    Output (dict):
      {
        "schedule": [ {staff_id, role, start_hour, end_hour, hours}, ... ],
        "per_hour": [ {hour, demand, assigned, understaff, overstaff}, ... ],
        "kpis": {
            "total_cost": float,
            "max_understaffing": int,
            "understaffed_hours": int,
            "avg_coverage_ratio": float,
            "fairness_score": float,
            "utilization_per_staff": [
                {staff_id, role, assigned_hours, max_hours, utilization}, ...
            ]
        }
      }
    """
    H = len(demand)
    if H == 0:
        raise ValueError("Demand list is empty")

    # 1) Sort staff by cost (cheapest first) → cost-efficient schedule
    staff_sorted = sorted(staff_list, key=lambda s: s.cost_per_hour)

    # 2) Track remaining hours per staff for the day
    remaining_hours: Dict[str, int] = {
        s.id: s.max_hours_per_day for s in staff_sorted
    }

    # 3) Hour → list of staff_ids assigned in that hour
    hour_assignments: Dict[int, List[str]] = {h: [] for h in range(H)}

    # 4) Greedy fill: for each hour, assign cheapest available staff
    for h in range(H):
        needed = max(0, demand[h])  # required staff count this hour
        for s in staff_sorted:
            if needed <= 0:
                break
            if remaining_hours[s.id] <= 0:
                continue

            # Assign this staff to this hour
            hour_assignments[h].append(s.id)
            remaining_hours[s.id] -= 1
            needed -= 1

    # 5) Convert hourly assignments into contiguous shifts per staff
    shifts = []
    for s in staff_sorted:
        current_start = None
        prev_h = None

        for h in range(H):
            if s.id in hour_assignments[h]:
                if current_start is None:
                    current_start = h
                prev_h = h
            else:
                # if we were in a shift, close it
                if current_start is not None:
                    shifts.append({
                        "staff_id": s.id,
                        "role": s.role,
                        "start_hour": current_start,
                        "end_hour": prev_h + 1,  # exclusive
                        "hours": (prev_h + 1) - current_start,
                    })
                    current_start = None
                    prev_h = None

        # close trailing shift if still open at end of day
        if current_start is not None:
            shifts.append({
                "staff_id": s.id,
                "role": s.role,
                "start_hour": current_start,
                "end_hour": prev_h + 1,
                "hours": (prev_h + 1) - current_start,
            })

    # 6) Per-hour coverage, under/over staffing
    coverage = [len(hour_assignments[h]) for h in range(H)]
    under = [max(0, demand[h] - coverage[h]) for h in range(H)]
    over = [max(0, coverage[h] - demand[h]) for h in range(H)]

    per_hour = [
        {
            "hour": h,
            "demand": demand[h],
            "assigned": coverage[h],
            "understaff": under[h],
            "overstaff": over[h],
        }
        for h in range(H)
    ]

    # 7) Utilization per staff
    utilization_list = []
    for s in staff_sorted:
        assigned_hours = sum(1 for h in range(H) if s.id in hour_assignments[h])
        utilization = (
            assigned_hours / s.max_hours_per_day
            if s.max_hours_per_day > 0
            else 0.0
        )

        utilization_list.append({
            "staff_id": s.id,
            "role": s.role,
            "assigned_hours": assigned_hours,
            "max_hours": s.max_hours_per_day,
            "utilization": round(utilization, 2),
        })

    # 8) Fairness score = 1 - stddev(utilization)  (0–1, higher = fairer)
    if utilization_list:
        util_values = [u["utilization"] for u in utilization_list]
        mean_u = sum(util_values) / len(util_values)
        var = sum((x - mean_u) ** 2 for x in util_values) / len(util_values)
        std = math.sqrt(var)
        fairness_score = round(max(0.0, 1.0 - std), 2)
    else:
        fairness_score = 0.0

    # 9) Total cost
    total_cost = 0.0
    for s in staff_sorted:
        assigned_hours = next(
            u["assigned_hours"] for u in utilization_list if u["staff_id"] == s.id
        )
        total_cost += assigned_hours * s.cost_per_hour

    # 10) KPI summary
    kpis = {
        "total_cost": total_cost,
        "max_understaffing": max(under) if under else 0,
        "understaffed_hours": sum(1 for x in under if x > 0),
        "avg_coverage_ratio": round(
            sum(min(coverage[h], demand[h]) for h in range(H)) / (sum(demand) or 1),
            2,
        ),
        "fairness_score": fairness_score,
        "utilization_per_staff": utilization_list,
    }

    return {
        "schedule": shifts,
        "per_hour": per_hour,
        "kpis": kpis,
    }


# -----------------------------
# Quick demo (you can delete later)
# -----------------------------
if __name__ == "__main__":
    # Example: 8-hour day, constant demand of 5 staff per hour
    demand = [5] * 8

    staff_list = [
        Staff(id="Nurse1", role="nurse", max_hours_per_day=8, cost_per_hour=300),
        Staff(id="Nurse2", role="nurse", max_hours_per_day=6, cost_per_hour=280),
        Staff(id="Doc1",   role="doctor", max_hours_per_day=4, cost_per_hour=800),
    ]

    result = optimize_staff_schedule(demand, staff_list)

    from pprint import pprint
    print("\n=== SHIFTS ===")
    pprint(result["schedule"])
    print("\n=== PER HOUR ===")
    pprint(result["per_hour"])
    print("\n=== KPIs ===")
    pprint(result["kpis"])
