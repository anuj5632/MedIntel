from dataclasses import dataclass, field
from typing import List


@dataclass
class CommunityAgentConfig:
    """
    Configuration for the Community Health Agent.

    You can tweak thresholds here without touching core logic.
    """

    default_languages: List[str] = field(default_factory=lambda: ["en"])
    default_location_name: str = "Your City"

    # Thresholds for severity classification
    aqi_advisory: int = 150
    aqi_alert: int = 200
    aqi_emergency: int = 300

    outbreak_advisory: float = 0.4
    outbreak_alert: float = 0.7
    outbreak_emergency: float = 0.9

    heat_index_advisory: float = 38.0
    heat_index_alert: float = 42.0
    heat_index_emergency: float = 45.0

    flood_risk_advisory: float = 0.3
    flood_risk_alert: float = 0.6
    flood_risk_emergency: float = 0.85
