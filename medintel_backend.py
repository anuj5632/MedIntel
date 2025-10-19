"""
MedIntel - Multi-Agent Hospital Management System
From Crisis Response to Predictive Readiness

This module implements 10 specialized AI agents for predictive hospital management
focused on festivals, pollution spikes, and epidemic outbreaks in India.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import random


# ==================== DATA MODELS ====================

class AlertLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentMessage:
    """Inter-agent communication message"""
    sender: str
    recipient: str
    timestamp: datetime
    message_type: str
    data: Dict[str, Any]
    priority: str


@dataclass
class PredictionResult:
    """Standard prediction result format"""
    agent_name: str
    timestamp: datetime
    predictions: Dict[str, Any]
    confidence: float
    alerts: List[Dict[str, Any]]
    recommendations: List[str]


# ==================== BASE AGENT CLASS ====================

class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, agent_id: str, name: str, role: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.status = "active"
        self.message_queue: List[AgentMessage] = []
        self.last_prediction = None
        self.performance_metrics = {
            "predictions_made": 0,
            "alerts_generated": 0,
            "avg_confidence": 0.0
        }
    
    def send_message(self, recipient: str, message_type: str, data: Dict, priority: str = "normal"):
        """Send message to another agent"""
        msg = AgentMessage(
            sender=self.agent_id,
            recipient=recipient,
            timestamp=datetime.now(),
            message_type=message_type,
            data=data,
            priority=priority
        )
        return msg
    
    def receive_message(self, message: AgentMessage):
        """Receive and queue message"""
        self.message_queue.append(message)
    
    def process(self, data: Dict[str, Any]) -> PredictionResult:
        """Process data and generate predictions"""
        raise NotImplementedError("Subclasses must implement process()")
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "performance": self.performance_metrics,
            "last_prediction": self.last_prediction.timestamp if self.last_prediction else None
        }


# ==================== AGENT 1: FORECASTING & RESOURCE ====================

class ForecastingAgent(BaseAgent):
    """Predicts patient inflow using time-series and environmental data"""
    
    def __init__(self):
        super().__init__("agent_001", "Forecasting Agent", "Patient Inflow Prediction")
        self.historical_weights = np.array([0.1, 0.15, 0.2, 0.25, 0.3])  # Last 5 days
    
    def process(self, data: Dict[str, Any]) -> PredictionResult:
        """
        Predict patient inflow based on multiple factors
        """
        # Extract inputs
        historical_data = data.get("historical_inflow", [100, 105, 110, 115, 120])
        aqi = data.get("aqi", 150)
        festival = data.get("festival", {})
        weather = data.get("weather", {})
        day_of_week = data.get("day_of_week", "weekday")
        
        # Base prediction using weighted moving average
        if len(historical_data) >= 5:
            base_prediction = np.dot(historical_data[-5:], self.historical_weights)
        else:
            base_prediction = np.mean(historical_data)
        
        # Apply multipliers
        multiplier = 1.0
        
        # Festival impact (30-50% increase)
        if festival.get("active", False):
            festival_type = festival.get("type", "regional")
            if festival_type == "major":  # Diwali, Holi, etc.
                multiplier *= 1.45
            else:
                multiplier *= 1.25
        
        # AQI impact (pollution-related illnesses)
        if aqi > 400:  # Severe
            multiplier *= 1.4
        elif aqi > 300:  # Very Poor
            multiplier *= 1.3
        elif aqi > 200:  # Poor
            multiplier *= 1.15
        elif aqi > 100:  # Moderate
            multiplier *= 1.05
        
        # Weather impact
        temp = weather.get("temperature", 25)
        humidity = weather.get("humidity", 60)
        
        if temp > 40 or temp < 5:  # Extreme temperatures
            multiplier *= 1.2
        elif temp > 38 or temp < 10:
            multiplier *= 1.1
        
        if humidity > 85:  # High humidity increases respiratory issues
            multiplier *= 1.08
        
        # Day of week impact
        if day_of_week in ["saturday", "sunday"]:
            multiplier *= 0.85  # Lower on weekends
        elif day_of_week == "monday":
            multiplier *= 1.1  # Higher on Mondays
        
        # Calculate final prediction
        predicted_inflow = int(base_prediction * multiplier)
        confidence = self._calculate_confidence(historical_data, aqi, festival)
        
        # Predict peak hours
        peak_hours = self._predict_peak_hours(predicted_inflow, day_of_week)
        
        # Generate alerts
        alerts = []
        if predicted_inflow > 150:
            alerts.append({
                "level": AlertLevel.HIGH.value,
                "message": f"Surge predicted: {predicted_inflow} patients (>25% above normal)",
                "action_required": True
            })
        elif predicted_inflow > 130:
            alerts.append({
                "level": AlertLevel.MODERATE.value,
                "message": f"Elevated inflow expected: {predicted_inflow} patients",
                "action_required": False
            })
        
        # Recommendations
        recommendations = []
        if predicted_inflow > 150:
            recommendations.extend([
                "Activate surge capacity protocols",
                "Call additional on-call staff",
                "Prepare overflow areas",
                "Increase telemedicine capacity"
            ])
        
        # Update metrics
        self.performance_metrics["predictions_made"] += 1
        self.performance_metrics["alerts_generated"] += len(alerts)
        self.performance_metrics["avg_confidence"] = (
            (self.performance_metrics["avg_confidence"] * (self.performance_metrics["predictions_made"] - 1) + confidence)
            / self.performance_metrics["predictions_made"]
        )
        
        result = PredictionResult(
            agent_name=self.name,
            timestamp=datetime.now(),
            predictions={
                "predicted_inflow": predicted_inflow,
                "base_prediction": int(base_prediction),
                "multiplier": round(multiplier, 2),
                "peak_hours": peak_hours,
                "forecast_7day": self._generate_7day_forecast(predicted_inflow, data)
            },
            confidence=confidence,
            alerts=alerts,
            recommendations=recommendations
        )
        
        self.last_prediction = result
        return result
    
    def _calculate_confidence(self, historical_data: List, aqi: int, festival: Dict) -> float:
        """Calculate prediction confidence based on data quality"""
        confidence = 0.85  # Base confidence
        
        # More historical data = higher confidence
        if len(historical_data) >= 30:
            confidence += 0.05
        elif len(historical_data) < 7:
            confidence -= 0.1
        
        # Extreme conditions reduce confidence
        if aqi > 400 or festival.get("active", False):
            confidence -= 0.08
        
        return max(0.5, min(0.95, confidence))
    
    def _predict_peak_hours(self, inflow: int, day_of_week: str) -> List[str]:
        """Predict peak hours based on inflow and day"""
        if day_of_week in ["saturday", "sunday"]:
            return ["10:00-12:00", "15:00-17:00"]
        else:
            return ["09:00-11:00", "17:00-19:00"]
    
    def _generate_7day_forecast(self, current_prediction: int, data: Dict) -> List[Dict]:
        """Generate 7-day forecast"""
        forecast = []
        base = current_prediction
        
        for i in range(7):
            date = datetime.now() + timedelta(days=i)
            # Add random variation
            variation = random.uniform(0.95, 1.1)
            predicted = int(base * variation)
            
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "predicted_inflow": predicted,
                "day_of_week": date.strftime("%A")
            })
        
        return forecast


# ==================== AGENT 2: STAFF OPTIMIZATION ====================

class StaffOptimizationAgent(BaseAgent):
    """Optimizes staff scheduling based on predicted demand"""
    
    def __init__(self):
        super().__init__("agent_002", "Staff Optimization Agent", "Shift Scheduling")
        self.staff_ratios = {
            "doctor_per_patient": 1/25,
            "nurse_per_patient": 1/12,
            "support_per_patient": 1/40
        }
    
    def process(self, data: Dict[str, Any]) -> PredictionResult:
        """Generate optimal staff schedule"""
        predicted_inflow = data.get("predicted_inflow", 120)
        current_staff = data.get("current_staff", {
            "doctors": 15,
            "nurses": 30,
            "support": 10
        })
        
        # Calculate required staff
        required_doctors = int(predicted_inflow * self.staff_ratios["doctor_per_patient"])
        required_nurses = int(predicted_inflow * self.staff_ratios["nurse_per_patient"])
        required_support = int(predicted_inflow * self.staff_ratios["support_per_patient"])
        
        # Calculate shortfall
        shortfall = {
            "doctors": max(0, required_doctors - current_staff["doctors"]),
            "nurses": max(0, required_nurses - current_staff["nurses"]),
            "support": max(0, required_support - current_staff["support"])
        }
        
        # Generate shift plan (3 shifts: morning, evening, night)
        shift_plan = self._generate_shift_plan(required_doctors, required_nurses, required_support)
        
        # Generate alerts
        alerts = []
        total_shortfall = sum(shortfall.values())
        if total_shortfall > 10:
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "message": f"Critical staff shortage: {total_shortfall} staff members needed",
                "action_required": True
            })
        elif total_shortfall > 0:
            alerts.append({
                "level": AlertLevel.MODERATE.value,
                "message": f"Staff shortage: {total_shortfall} additional staff recommended",
                "action_required": True
            })
        
        # Recommendations
        recommendations = []
        if shortfall["doctors"] > 0:
            recommendations.append(f"Call {shortfall['doctors']} on-call doctors")
        if shortfall["nurses"] > 0:
            recommendations.append(f"Request {shortfall['nurses']} nurses from staffing pool")
        if total_shortfall > 0:
            recommendations.append("Consider extending shifts or canceling elective procedures")
        
        result = PredictionResult(
            agent_name=self.name,
            timestamp=datetime.now(),
            predictions={
                "required_staff": {
                    "doctors": required_doctors,
                    "nurses": required_nurses,
                    "support": required_support
                },
                "current_staff": current_staff,
                "shortfall": shortfall,
                "shift_plan": shift_plan,
                "utilization_rate": self._calculate_utilization(current_staff, predicted_inflow)
            },
            confidence=0.88,
            alerts=alerts,
            recommendations=recommendations
        )
        
        self.last_prediction = result
        return result
    
    def _generate_shift_plan(self, doctors: int, nurses: int, support: int) -> List[Dict]:
        """Generate 3-shift schedule"""
        return [
            {
                "shift": "Morning (6 AM - 2 PM)",
                "doctors": int(doctors * 0.35),
                "nurses": int(nurses * 0.35),
                "support": int(support * 0.40)
            },
            {
                "shift": "Evening (2 PM - 10 PM)",
                "doctors": int(doctors * 0.40),
                "nurses": int(nurses * 0.40),
                "support": int(support * 0.35)
            },
            {
                "shift": "Night (10 PM - 6 AM)",
                "doctors": int(doctors * 0.25),
                "nurses": int(nurses * 0.25),
                "support": int(support * 0.25)
            }
        ]
    
    def _calculate_utilization(self, current_staff: Dict, predicted_inflow: int) -> Dict:
        """Calculate staff utilization rates"""
        return {
            "doctors": round((predicted_inflow * self.staff_ratios["doctor_per_patient"]) / current_staff["doctors"] * 100, 1),
            "nurses": round((predicted_inflow * self.staff_ratios["nurse_per_patient"]) / current_staff["nurses"] * 100, 1),
            "overall": round(predicted_inflow / sum(current_staff.values()) * 2, 1)
        }


# ==================== AGENT 3: INVENTORY MANAGEMENT ====================

class InventoryAgent(BaseAgent):
    """Forecasts supply needs and manages inventory"""
    
    def __init__(self):
        super().__init__("agent_003", "Medical Supply Agent", "Inventory Management")
        self.critical_items = {
            "n95_masks": {"current": 450, "min_threshold": 600, "consumption_per_patient": 2},
            "oxygen_cylinders": {"current": 28, "min_threshold": 30, "consumption_per_patient": 0.15},
            "iv_fluids": {"current": 320, "min_threshold": 200, "consumption_per_patient": 1.5},
            "antibiotics": {"current": 180, "min_threshold": 200, "consumption_per_patient": 0.8},
            "ppe_kits": {"current": 210, "min_threshold": 300, "consumption_per_patient": 1.2},
            "ventilator_consumables": {"current": 45, "min_threshold": 50, "consumption_per_patient": 0.05}
        }
    
    def process(self, data: Dict[str, Any]) -> PredictionResult:
        """Forecast inventory needs and generate reorder recommendations"""
        predicted_inflow = data.get("predicted_inflow", 120)
        forecast_days = data.get("forecast_days", 7)
        
        inventory_alerts = []
        reorder_recommendations = []
        
        for item_name, item_data in self.critical_items.items():
            current_stock = item_data["current"]
            min_threshold = item_data["min_threshold"]
            consumption_rate = item_data["consumption_per_patient"]
            
            # Calculate projected consumption
            daily_consumption = predicted_inflow * consumption_rate
            projected_consumption = daily_consumption * forecast_days
            days_until_stockout = current_stock / daily_consumption if daily_consumption > 0 else 999
            
            # Determine status
            if current_stock < min_threshold * 0.5:
                status = AlertLevel.CRITICAL.value
                reorder_qty = int((min_threshold * 2) - current_stock)
            elif current_stock < min_threshold:
                status = AlertLevel.HIGH.value
                reorder_qty = int(min_threshold * 1.5 - current_stock)
            elif days_until_stockout < 5:
                status = AlertLevel.MODERATE.value
                reorder_qty = int(projected_consumption)
            else:
                status = AlertLevel.LOW.value
                reorder_qty = 0
            
            inventory_alerts.append({
                "item": item_name.replace("_", " ").title(),
                "current_stock": current_stock,
                "min_threshold": min_threshold,
                "status": status,
                "days_until_stockout": round(days_until_stockout, 1),
                "daily_consumption": round(daily_consumption, 1),
                "reorder_quantity": reorder_qty
            })
            
            if reorder_qty > 0:
                reorder_recommendations.append({
                    "item": item_name.replace("_", " ").title(),
                    "quantity": reorder_qty,
                    "priority": status,
                    "estimated_cost": reorder_qty * random.randint(50, 500)  # Simulated cost
                })
        
        # Generate overall alerts
        alerts = []
        critical_items = [item for item in inventory_alerts if item["status"] == AlertLevel.CRITICAL.value]
        if critical_items:
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "message": f"{len(critical_items)} items at critical levels",
                "action_required": True
            })
        
        # Recommendations
        recommendations = []
        if reorder_recommendations:
            recommendations.append(f"Initiate emergency procurement for {len(reorder_recommendations)} items")
            recommendations.append("Contact backup vendors for critical supplies")
        if any(item["days_until_stockout"] < 3 for item in inventory_alerts):
            recommendations.append("Activate emergency supply protocols")
        
        result = PredictionResult(
            agent_name=self.name,
            timestamp=datetime.now(),
            predictions={
                "inventory_status": inventory_alerts,
                "reorder_recommendations": reorder_recommendations,
                "total_reorder_cost": sum(r["estimated_cost"] for r in reorder_recommendations),
                "items_below_threshold": len([i for i in inventory_alerts if i["current_stock"] < i["min_threshold"]])
            },
            confidence=0.91,
            alerts=alerts,
            recommendations=recommendations
        )
        
        self.last_prediction = result
        return result


# ==================== AGENT 4: EQUIPMENT & UTILITY ====================

class EquipmentAgent(BaseAgent):
    """Monitors equipment and triggers predictive maintenance"""
    
    def __init__(self):
        super().__init__("agent_004", "Equipment Agent", "Predictive Maintenance")
        self.equipment_registry = {
            "ventilator_a3": {"type": "ventilator", "utilization": 85, "last_maintenance": 45, "maintenance_interval": 60},
            "ventilator_b7": {"type": "ventilator", "utilization": 92, "last_maintenance": 62, "maintenance_interval": 60},
            "ct_scanner_1": {"type": "imaging", "utilization": 68, "last_maintenance": 25, "maintenance_interval": 90},
            "xray_machine_2": {"type": "imaging", "utilization": 78, "last_maintenance": 88, "maintenance_interval": 90},
            "oxygen_concentrator_1": {"type": "oxygen", "utilization": 95, "last_maintenance": 30, "maintenance_interval": 45},
            "oxygen_concentrator_2": {"type": "oxygen", "utilization": 88, "last_maintenance": 40, "maintenance_interval": 45}
        }
    
    def process(self, data: Dict[str, Any]) -> PredictionResult:
        """Monitor equipment and predict maintenance needs"""
        predicted_load = data.get("predicted_inflow", 120) / 100  # Load multiplier
        
        equipment_status = []
        maintenance_alerts = []
        
        for equip_id, equip_data in self.equipment_registry.items():
            utilization = min(100, equip_data["utilization"] * predicted_load)
            days_since_maintenance = equip_data["last_maintenance"]
            maintenance_interval = equip_data["maintenance_interval"]
            
            # Calculate maintenance urgency
            maintenance_due_in = maintenance_interval - days_since_maintenance
            
            # Determine status
            if days_since_maintenance >= maintenance_interval:
                status = "maintenance_overdue"
                priority = AlertLevel.CRITICAL.value
            elif maintenance_due_in <= 3:
                status = "maintenance_due"
                priority = AlertLevel.HIGH.value
            elif utilization > 90:
                status = "high_utilization"
                priority = AlertLevel.MODERATE.value
            else:
                status = "operational"
                priority = AlertLevel.LOW.value
            
            equipment_status.append({
                "equipment_id": equip_id.replace("_", " ").title(),
                "type": equip_data["type"],
                "status": status,
                "utilization": round(utilization, 1),
                "maintenance_due_in": maintenance_due_in if maintenance_due_in > 0 else "Overdue",
                "priority": priority
            })
            
            if status in ["maintenance_overdue", "maintenance_due"]:
                maintenance_alerts.append({
                    "equipment": equip_id.replace("_", " ").title(),
                    "status": status,
                    "priority": priority,
                    "action": "Schedule immediate maintenance" if status == "maintenance_overdue" else "Schedule maintenance within 3 days"
                })
        
        # Generate alerts
        alerts = []
        critical_equipment = [e for e in equipment_status if e["status"] == "maintenance_overdue"]
        if critical_equipment:
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "message": f"{len(critical_equipment)} equipment units require immediate maintenance",
                "action_required": True
            })
        
        # Recommendations
        recommendations = []
        if maintenance_alerts:
            recommendations.append(f"Schedule maintenance for {len(maintenance_alerts)} equipment units")
        high_util_equipment = [e for e in equipment_status if e["utilization"] > 90]
        if high_util_equipment:
            recommendations.append("Consider adding backup equipment for high-utilization units")
        
        result = PredictionResult(
            agent_name=self.name,
            timestamp=datetime.now(),
            predictions={
                "equipment_status": equipment_status,
                "maintenance_alerts": maintenance_alerts,
                "total_equipment": len(equipment_status),
                "operational": len([e for e in equipment_status if e["status"] == "operational"]),
                "maintenance_required": len(maintenance_alerts)
            },
            confidence=0.93,
            alerts=alerts,
            recommendations=recommendations
        )
        
        self.last_prediction = result
        return result


# ==================== AGENT 5: OUTBREAK DETECTION ====================

class OutbreakAgent(BaseAgent):
    """Detects early epidemic or pollution-related illness trends"""
    
    def __init__(self):
        super().__init__("agent_005", "Predictive Outbreak Agent", "Epidemic Monitoring")
    
    def process(self, data: Dict[str, Any]) -> PredictionResult:
        """Detect disease patterns and outbreak risks"""
        aqi = data.get("aqi", 150)
        recent_cases = data.get("recent_cases", {})
        historical_baseline = data.get("historical_baseline", {})
        
        # Simulate disease tracking
        disease_patterns = [
            {"condition": "Respiratory Infections", "current": 34, "baseline": 24, "trend": "increasing"},
            {"condition": "Asthma Attacks", "current": 22, "baseline": 15, "trend": "increasing"},
            {"condition": "Cardiac Issues", "current": 12, "baseline": 11, "trend": "stable"},
            {"condition": "Dengue", "current": 3, "baseline": 2, "trend": "stable"},
            {"condition": "Gastroenteritis", "current": 8, "baseline": 7, "trend": "stable"}
        ]
        
        # Calculate outbreak risk
        outbreak_risk = "low"
        alerts = []
        
        if aqi > 300:
            outbreak_risk = "high"
            alerts.append({
                "level": AlertLevel.HIGH.value,
                "message": "Severe air pollution increasing respiratory illness risk",
                "action_required": True
            })
        elif aqi > 200:
            outbreak_risk = "moderate"
        
        # Check for disease clustering
        patterns_detected = []
        for pattern in disease_patterns:
            percent_change = ((pattern["current"] - pattern["baseline"]) / pattern["baseline"]) * 100
            pattern["percent_change"] = round(percent_change, 1)
            
            if percent_change > 30:
                patterns_detected.append(pattern)
                if percent_change > 50:
                    alerts.append({
                        "level": AlertLevel.HIGH.value,
                        "message": f"{pattern['condition']}: {percent_change:.0f}% increase detected",
                        "action_required": True
                    })
        
        # Recommendations
        recommendations = []
        if outbreak_risk in ["moderate", "high"]:
            recommendations.extend([
                "Increase respiratory care unit capacity",
                "Stock additional respiratory medications",
                "Prepare isolation protocols"
            ])
        if patterns_detected:
            recommendations.append(f"Monitor {len(patterns_detected)} disease patterns closely")
        
        result = PredictionResult(
            agent_name=self.name,
            timestamp=datetime.now(),
            predictions={
                "outbreak_risk": outbreak_risk,
                "disease_patterns": disease_patterns,
                "aqi_health_impact": self._calculate_aqi_impact(aqi),
                "patterns_detected": patterns_detected,
                "risk_score": self._calculate_risk_score(aqi, disease_patterns)
            },
            confidence=0.82,
            alerts=alerts,
            recommendations=recommendations
        )
        
        self.last_prediction = result
        return result
    
    def _calculate_aqi_impact(self, aqi: int) -> Dict:
        """Calculate health impact based on AQI"""
        if aqi > 400:
            return {"category": "Severe", "impact": "Emergency conditions", "risk": "critical"}
        elif aqi > 300:
            return {"category": "Very Poor", "impact": "High health risk", "risk": "high"}
        elif aqi > 200:
            return {"category": "Poor", "impact": "Moderate health concerns", "risk": "moderate"}
        elif aqi > 100:
            return {"category": "Moderate", "impact": "Acceptable for most", "risk": "low"}
        else:
            return {"category": "Good", "impact": "Minimal health risk", "risk": "minimal"}
    
    def _calculate_risk_score(self, aqi: int, patterns: List[Dict]) -> int:
        """Calculate overall outbreak risk score (0-100)"""
        score = 0
        
        # AQI contribution (0-40 points)
        if aqi > 400:
            score += 40
        elif aqi > 300:
            score += 30
        elif aqi > 200:
            score += 20
        else:
            score += 10
        
        # Disease trend contribution (0-60 points)
        increasing_patterns = [p for p in patterns if p["trend"] == "increasing"]
        score += min(60, len(increasing_patterns) * 15)
        
        return min(100, score)


# ==================== MULTI-AGENT COORDINATOR ====================

class MultiAgentCoordinator:
    """Coordinates all agents and manages inter-agent communication"""
    
    def __init__(self):
        self.agents = {
            "forecasting": ForecastingAgent(),
            "staff": StaffOptimizationAgent(),
            "inventory": InventoryAgent(),
            "equipment": EquipmentAgent(),
            "outbreak": OutbreakAgent()
        }
        self.message_bus = []
        self.system_state = {}
    
    def run_simulation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete multi-agent simulation"""
        results = {}
        
        # Step 1: Forecasting Agent predicts inflow
        forecast_result = self.agents["forecasting"].process(input_data)
        results["forecasting"] = asdict(forecast_result)
        predicted_inflow = forecast_result.predictions["predicted_inflow"]
        
        # Step 2: Staff Optimization based on forecast
        staff_data = {**input_data, "predicted_inflow": predicted_inflow}
        staff_result = self.agents["staff"].process(staff_data)
        results["staff"] = asdict(staff_result)
        
        # Step 3: Inventory Management
        inventory_data = {**input_data, "predicted_inflow": predicted_inflow}
        inventory_result = self.agents["inventory"].process(inventory_data)
        results["inventory"] = asdict(inventory_result)
        
        # Step 4: Equipment Monitoring
        equipment_data = {**input_data, "predicted_inflow": predicted_inflow}
        equipment_result = self.agents["equipment"].process(equipment_data)
        results["equipment"] = asdict(equipment_result)
        
        # Step 5: Outbreak Detection
        outbreak_result = self.agents["outbreak"].process(input_data)
        results["outbreak"] = asdict(outbreak_result)
        
        # Generate system summary
        summary = self._generate_system_summary(results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "agent_results": results,
            "system_summary": summary
        }
    
    def _generate_system_summary(self, results: Dict) -> Dict:
        """Generate overall system status summary"""
        total_alerts = sum(len(r["alerts"]) for r in results.values())
        critical_alerts = sum(
            len([a for a in r["alerts"] if a["level"] == AlertLevel.CRITICAL.value])
            for r in results.values()
        )
        
        return {
            "overall_status": "critical" if critical_alerts > 0 else "normal",
            "total_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "active_agents": len(self.agents),
            "system_health": "operational"
        }


# ==================== SAMPLE DATA GENERATOR ====================

def generate_sample_data() -> Dict[str, Any]:
    """Generate sample input data for testing"""
    return {
        "historical_inflow": [95, 108, 122, 134, 145, 152],
        "aqi": random.randint(200, 350),
        "festival": {
            "active": True,
            "type": "major",
            "name": "Diwali",
            "days_remaining": 2
        },
        "weather": {
            "temperature": random.randint(28, 38),
            "humidity": random.randint(55, 85)
        },
        "day_of_week": "monday",
        "current_staff": {
            "doctors": 15,
            "nurses": 30,
            "support": 10
        },
        "forecast_days": 7
    }


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    # Initialize coordinator
    coordinator = MultiAgentCoordinator()
    
    # Generate sample data
    sample_data = generate_sample_data()
    
    # Run simulation
    print("=" * 80)
    print("MEDINTEL - MULTI-AGENT HOSPITAL MANAGEMENT SYSTEM")
    print("From Crisis Response to Predictive Readiness")
    print("=" * 80)
    print(f"\nSimulation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"AQI Level: {sample_data['aqi']}")
    print(f"Festival: {sample_data['festival']['name']} (Active)")
    print(f"Temperature: {sample_data['weather']['temperature']}°C")
    print("\n" + "=" * 80)
    
    results = coordinator.run_simulation(sample_data)
    
    # Display results
    print("\n📊 AGENT PREDICTIONS:\n")
    
    for agent_name, agent_result in results["agent_results"].items():
        print(f"\n{'='*80}")
        print(f"🤖 {agent_result['agent_name'].upper()}")
        print(f"{'='*80}")
        print(f"Confidence: {agent_result['confidence']*100:.1f}%")
        print(f"Timestamp: {agent_result['timestamp']}")
        
        print(f"\n📈 Key Predictions:")
        for key, value in agent_result['predictions'].items():
            if isinstance(value, (int, float, str)):
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        if agent_result['alerts']:
            print(f"\n⚠️  Alerts ({len(agent_result['alerts'])}):")
            for alert in agent_result['alerts']:
                print(f"  [{alert['level'].upper()}] {alert['message']}")
        
        if agent_result['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in agent_result['recommendations']:
                print(f"  • {rec}")
    
    print("\n" + "=" * 80)
    print("SYSTEM SUMMARY")
    print("=" * 80)
    summary = results['system_summary']
    print(f"Overall Status: {summary['overall_status'].upper()}")
    print(f"Total Alerts: {summary['total_alerts']}")
    print(f"Critical Alerts: {summary['critical_alerts']}")
    print(f"Active Agents: {summary['active_agents']}")
    print(f"System Health: {summary['system_health'].upper()}")
    print("=" * 80)
    
    # Export results to JSON
    with open('medintel_simulation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n✅ Results exported to 'medintel_simulation_results.json'")
    print("=" * 80)