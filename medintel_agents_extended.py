"""
MedIntel - Extended Agent Implementation (Agents 6-10)
Telemedicine, Emergency, Coordination, Supply Chain, and Community Health
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from enum import Enum


class AlertLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


# ==================== AGENT 6: TELEMEDICINE & TRIAGE ====================

class TelemedicineAgent:
    """Routes mild cases to teleconsultation to reduce overcrowding"""
    
    def __init__(self):
        self.agent_id = "agent_006"
        self.name = "Telemedicine Agent"
        self.role = "Remote Triage"
        self.triage_protocols = {
            "mild": {"action": "telemedicine", "priority": 3},
            "moderate": {"action": "schedule_visit", "priority": 2},
            "severe": {"action": "immediate_er", "priority": 1}
        }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Triage patients and route to appropriate care channels"""
        predicted_inflow = data.get("predicted_inflow", 120)
        current_er_capacity = data.get("er_capacity", 50)
        
        # Simulate patient triage distribution
        mild_cases = int(predicted_inflow * 0.52)  # 52% mild
        moderate_cases = int(predicted_inflow * 0.32)  # 32% moderate
        severe_cases = int(predicted_inflow * 0.16)  # 16% severe
        
        # Calculate telemedicine diversion
        telemedicine_diverted = int(mild_cases * 0.85)  # 85% of mild cases
        in_person_required = moderate_cases + severe_cases + (mild_cases - telemedicine_diverted)
        
        diversion_rate = (telemedicine_diverted / predicted_inflow) * 100
        
        # Calculate capacity impact
        er_load_reduction = (telemedicine_diverted / current_er_capacity) * 100
        
        # Telemedicine capacity planning
        tele_doctors_needed = int(telemedicine_diverted / 15)  # 15 patients per doctor
        
        # Generate alerts
        alerts = []
        if diversion_rate < 40:
            alerts.append({
                "level": AlertLevel.MODERATE.value,
                "message": f"Low telemedicine diversion rate: {diversion_rate:.1f}%",
                "action_required": True
            })
        
        if in_person_required > current_er_capacity:
            alerts.append({
                "level": AlertLevel.HIGH.value,
                "message": f"In-person cases ({in_person_required}) exceed ER capacity ({current_er_capacity})",
                "action_required": True
            })
        
        # Recommendations
        recommendations = []
        recommendations.append(f"Allocate {tele_doctors_needed} doctors to telemedicine")
        if diversion_rate > 60:
            recommendations.append("Excellent triage - maintain current protocols")
        else:
            recommendations.append("Increase telemedicine awareness campaigns")
        
        if severe_cases > 20:
            recommendations.append("Prepare fast-track ER protocols for severe cases")
        
        return {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "total_cases": predicted_inflow,
                "mild_cases": mild_cases,
                "moderate_cases": moderate_cases,
                "severe_cases": severe_cases,
                "telemedicine_diverted": telemedicine_diverted,
                "in_person_required": in_person_required,
                "diversion_rate": round(diversion_rate, 1),
                "er_load_reduction": round(er_load_reduction, 1),
                "tele_doctors_needed": tele_doctors_needed,
                "avg_consultation_time": "12 minutes",
                "patient_satisfaction": 87
            },
            "confidence": 0.89,
            "alerts": alerts,
            "recommendations": recommendations
        }


# ==================== AGENT 7: EMERGENCY READINESS ====================

class EmergencyAgent:
    """Activates surge protocols and allocates ICU/critical care resources"""
    
    def __init__(self):
        self.agent_id = "agent_007"
        self.name = "Emergency Readiness Agent"
        self.role = "Surge Protocol"
        self.icu_capacity = {"total_beds": 24, "occupied": 18, "ventilators": 20}
        self.er_capacity = {"beds": 50, "trauma_bays": 6}
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage emergency preparedness and surge capacity"""
        predicted_inflow = data.get("predicted_inflow", 120)
        severe_cases = data.get("severe_cases", 20)
        outbreak_risk = data.get("outbreak_risk", "low")
        
        # Determine surge activation
        surge_threshold = 150
        surge_activated = predicted_inflow > surge_threshold
        
        # Calculate resource allocation
        icu_available = self.icu_capacity["total_beds"] - self.icu_capacity["occupied"]
        icu_demand = int(severe_cases * 0.3)  # 30% of severe cases need ICU
        
        ventilator_available = self.icu_capacity["ventilators"] - int(self.icu_capacity["occupied"] * 0.7)
        ventilator_demand = int(icu_demand * 0.6)  # 60% of ICU patients need ventilators
        
        # Determine ER status code
        if predicted_inflow > 180:
            er_status = "Code Red"
            er_level = AlertLevel.CRITICAL.value
        elif predicted_inflow > 150:
            er_status = "Code Orange"
            er_level = AlertLevel.HIGH.value
        elif predicted_inflow > 130:
            er_status = "Code Yellow"
            er_level = AlertLevel.MODERATE.value
        else:
            er_status = "Code Green"
            er_level = AlertLevel.LOW.value
        
        # Generate alerts
        alerts = []
        if surge_activated:
            alerts.append({
                "level": AlertLevel.HIGH.value,
                "message": f"SURGE PROTOCOL ACTIVATED - Patient inflow: {predicted_inflow}",
                "action_required": True
            })
        
        if icu_demand > icu_available:
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "message": f"ICU capacity exceeded - Need: {icu_demand}, Available: {icu_available}",
                "action_required": True
            })
        
        if ventilator_demand > ventilator_available:
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "message": f"Ventilator shortage - Need: {ventilator_demand}, Available: {ventilator_available}",
                "action_required": True
            })
        
        # Recommendations
        recommendations = []
        if surge_activated:
            recommendations.extend([
                "Activate overflow ward in conference center",
                "Call all on-call physicians and specialists",
                "Expedite discharge of stable patients",
                "Cancel elective procedures for next 24 hours",
                "Coordinate with nearby hospitals for transfers"
            ])
        
        if icu_demand > icu_available:
            recommendations.append("Convert post-op recovery beds to ICU capacity")
        
        if outbreak_risk in ["moderate", "high"]:
            recommendations.append("Prepare isolation wards and negative pressure rooms")
        
        # Calculate response time estimates
        response_times = {
            "ambulance_avg": "8 minutes",
            "er_triage": "5 minutes",
            "icu_admission": "15 minutes",
            "surgery_prep": "30 minutes"
        }
        
        return {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "surge_activated": surge_activated,
                "er_status": er_status,
                "er_status_level": er_level,
                "icu_availability": {
                    "total": self.icu_capacity["total_beds"],
                    "occupied": self.icu_capacity["occupied"],
                    "available": icu_available,
                    "demand": icu_demand,
                    "shortfall": max(0, icu_demand - icu_available)
                },
                "ventilator_status": {
                    "available": ventilator_available,
                    "demand": ventilator_demand,
                    "utilization_percent": round((self.icu_capacity["ventilators"] - ventilator_available) / self.icu_capacity["ventilators"] * 100, 1)
                },
                "er_beds_available": self.er_capacity["beds"] - int(predicted_inflow * 0.2),
                "trauma_bays_available": self.er_capacity["trauma_bays"] - 2,
                "response_times": response_times,
                "disaster_level": "Level 2" if surge_activated else "Level 0"
            },
            "confidence": 0.91,
            "alerts": alerts,
            "recommendations": recommendations
        }


# ==================== AGENT 8: COORDINATION ====================

class CoordinationAgent:
    """Synchronizes data between departments and ambulance services"""
    
    def __init__(self):
        self.agent_id = "agent_008"
        self.name = "Coordination Agent"
        self.role = "Inter-department Sync"
        self.departments = ["Emergency", "ICU", "General Ward", "Outpatient", "Surgery", "Imaging"]
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate between departments and external services"""
        predicted_inflow = data.get("predicted_inflow", 120)
        surge_activated = data.get("surge_activated", False)
        
        # Simulate department load distribution
        department_loads = {
            "Emergency": int(predicted_inflow * 0.35),
            "ICU": int(predicted_inflow * 0.08),
            "General Ward": int(predicted_inflow * 0.25),
            "Outpatient": int(predicted_inflow * 0.20),
            "Surgery": int(predicted_inflow * 0.07),
            "Imaging": int(predicted_inflow * 0.05)
        }
        
        # Calculate department utilization
        department_capacity = {
            "Emergency": 50,
            "ICU": 24,
            "General Ward": 100,
            "Outpatient": 80,
            "Surgery": 15,
            "Imaging": 30
        }
        
        department_status = []
        for dept in self.departments:
            load = department_loads[dept]
            capacity = department_capacity[dept]
            utilization = (load / capacity) * 100
            
            if utilization > 90:
                status = "critical"
            elif utilization > 75:
                status = "high"
            elif utilization > 60:
                status = "moderate"
            else:
                status = "normal"
            
            department_status.append({
                "department": dept,
                "load": load,
                "capacity": capacity,
                "utilization": round(utilization, 1),
                "status": status
            })
        
        # Ambulance coordination
        ambulance_queue = random.randint(2, 8) if surge_activated else random.randint(0, 4)
        ambulance_eta = [f"{random.randint(3, 15)} min" for _ in range(ambulance_queue)]
        
        # Inter-department transfers
        transfer_queue = random.randint(5, 15) if surge_activated else random.randint(2, 7)
        
        # External coordination
        external_coordination = {
            "ambulance_services": "Coordinated with 3 services",
            "nearby_hospitals": "2 hospitals on standby for overflow",
            "blood_bank": "Adequate reserves",
            "police_coordination": "Traffic clearance arranged" if surge_activated else "Standard protocol"
        }
        
        # Generate alerts
        alerts = []
        critical_depts = [d for d in department_status if d["status"] == "critical"]
        if critical_depts:
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "message": f"{len(critical_depts)} departments at critical capacity",
                "action_required": True
            })
        
        if ambulance_queue > 5:
            alerts.append({
                "level": AlertLevel.HIGH.value,
                "message": f"High ambulance queue: {ambulance_queue} incoming",
                "action_required": True
            })
        
        # Recommendations
        recommendations = []
        if critical_depts:
            recommendations.append(f"Redistribute load from {', '.join([d['department'] for d in critical_depts])}")
        if ambulance_queue > 5:
            recommendations.append("Prepare fast-track ambulance bay")
        if transfer_queue > 10:
            recommendations.append("Expedite inter-department transfer protocols")
        
        return {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "department_status": department_status,
                "ambulance_queue": ambulance_queue,
                "ambulance_eta_list": ambulance_eta,
                "inter_department_transfers": transfer_queue,
                "external_coordination": external_coordination,
                "bed_allocation": {
                    "emergency_available": department_capacity["Emergency"] - department_loads["Emergency"],
                    "icu_available": department_capacity["ICU"] - department_loads["ICU"],
                    "general_ward_available": department_capacity["General Ward"] - department_loads["General Ward"]
                },
                "coordination_score": 85,
                "response_time_avg": "6.5 minutes"
            },
            "confidence": 0.87,
            "alerts": alerts,
            "recommendations": recommendations
        }


# ==================== AGENT 9: SUPPLY CHAIN RESILIENCE ====================

class SupplyChainAgent:
    """Detects vendor delays and suggests alternate sourcing"""
    
    def __init__(self):
        self.agent_id = "agent_009"
        self.name = "Supply Chain Resilience Agent"
        self.role = "Vendor Management"
        self.vendors = {
            "MedSupply Co.": {"reliability": 95, "delivery_time": 24, "items": ["PPE", "Masks"]},
            "Pharma Direct": {"reliability": 78, "delivery_time": 48, "items": ["Antibiotics", "IV Fluids"]},
            "Equipment Plus": {"reliability": 92, "delivery_time": 36, "items": ["Medical Devices"]},
            "OxyGen Systems": {"reliability": 88, "delivery_time": 12, "items": ["Oxygen"]},
            "Surgical Supplies Inc": {"reliability": 90, "delivery_time": 24, "items": ["Surgical Equipment"]}
        }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor supply chain and recommend alternatives"""
        inventory_alerts = data.get("inventory_alerts", [])
        predicted_inflow = data.get("predicted_inflow", 120)
        
        # Simulate vendor performance
        vendor_status = []
        delays_detected = []
        
        for vendor_name, vendor_info in self.vendors.items():
            # Simulate occasional delays
            is_delayed = random.random() > (vendor_info["reliability"] / 100)
            delay_hours = random.randint(12, 72) if is_delayed else 0
            
            status = "delayed" if is_delayed else "on-time"
            
            vendor_status.append({
                "vendor": vendor_name,
                "status": status,
                "reliability": vendor_info["reliability"],
                "expected_delivery": vendor_info["delivery_time"],
                "delay_hours": delay_hours if is_delayed else None,
                "items_supplied": vendor_info["items"]
            })
            
            if is_delayed:
                delays_detected.append(vendor_name)
        
        # Identify alternate sources
        alternate_sources = []
        for delayed_vendor in delays_detected:
            delayed_items = self.vendors[delayed_vendor]["items"]
            
            # Find alternate vendors for same items
            alternates = [
                v for v, info in self.vendors.items()
                if v != delayed_vendor and any(item in info["items"] for item in delayed_items)
            ]
            
            if alternates:
                alternate_sources.append({
                    "original_vendor": delayed_vendor,
                    "delayed_items": delayed_items,
                    "alternate_vendors": alternates[:2],  # Top 2 alternates
                    "action": "Switch to alternate vendor"
                })
        
        # Calculate supply chain risk
        avg_reliability = sum(v["reliability"] for v in self.vendors.values()) / len(self.vendors)
        risk_score = 100 - avg_reliability
        
        if risk_score > 20:
            risk_level = "high"
        elif risk_score > 10:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        # Generate alerts
        alerts = []
        if delays_detected:
            alerts.append({
                "level": AlertLevel.HIGH.value if len(delays_detected) > 2 else AlertLevel.MODERATE.value,
                "message": f"{len(delays_detected)} vendors experiencing delays",
                "action_required": True
            })
        
        critical_inventory = [item for item in inventory_alerts if item.get("status") == "critical"]
        if critical_inventory and delays_detected:
            alerts.append({
                "level": AlertLevel.CRITICAL.value,
                "message": "Critical inventory items affected by vendor delays",
                "action_required": True
            })
        
        # Recommendations
        recommendations = []
        if alternate_sources:
            recommendations.append(f"Activate {len(alternate_sources)} alternate vendors immediately")
        if risk_level in ["moderate", "high"]:
            recommendations.append("Increase safety stock for critical items")
            recommendations.append("Diversify vendor base to reduce dependency")
        if delays_detected:
            recommendations.append("Expedite shipments with premium delivery options")
        
        return {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "vendor_status": vendor_status,
                "delays_detected": len(delays_detected),
                "affected_vendors": delays_detected,
                "alternate_sources": alternate_sources,
                "supply_chain_risk": risk_level,
                "risk_score": round(risk_score, 1),
                "avg_reliability": round(avg_reliability, 1),
                "estimated_impact": f"{len(delays_detected) * 24} hours delay" if delays_detected else "No impact",
                "contingency_plan": "Active" if alternate_sources else "Not required"
            },
            "confidence": 0.86,
            "alerts": alerts,
            "recommendations": recommendations
        }


# ==================== AGENT 10: COMMUNITY HEALTH ====================

class CommunityHealthAgent:
    """Sends verified advisories and alerts to patients in local languages"""
    
    def __init__(self):
        self.agent_id = "agent_010"
        self.name = "Community Health Agent"
        self.role = "Public Advisories"
        self.languages = ["Hindi", "Marathi", "English", "Tamil", "Telugu"]
        self.communication_channels = ["WhatsApp", "SMS", "Email", "Mobile App", "Voice Call"]
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and distribute public health advisories"""
        aqi = data.get("aqi", 150)
        outbreak_risk = data.get("outbreak_risk", "low")
        festival = data.get("festival", {})
        surge_activated = data.get("surge_activated", False)
        
        # Generate advisory content
        advisories = []
        
        # AQI-based advisory
        if aqi > 300:
            advisories.append({
                "type": "air_quality",
                "priority": "high",
                "message": "SEVERE air pollution detected. Wear N95 masks outdoors. Avoid outdoor activities. Keep windows closed.",
                "target_audience": "all",
                "urgency": "immediate"
            })
        elif aqi > 200:
            advisories.append({
                "type": "air_quality",
                "priority": "moderate",
                "message": "HIGH air pollution levels. Sensitive groups should limit outdoor exposure. Wear masks recommended.",
                "target_audience": "sensitive_groups",
                "urgency": "today"
            })
        
        # Outbreak advisory
        if outbreak_risk in ["moderate", "high"]:
            advisories.append({
                "type": "outbreak_alert",
                "priority": "high",
                "message": "Increased respiratory infections reported. Practice hand hygiene. Seek medical attention if experiencing symptoms.",
                "target_audience": "all",
                "urgency": "immediate"
            })
        
        # Hospital capacity advisory
        if surge_activated:
            advisories.append({
                "type": "hospital_capacity",
                "priority": "high",
                "message": "Hospital experiencing high patient volume. Non-emergency cases: Please use telemedicine services. Emergency cases: Call ahead.",
                "target_audience": "all",
                "urgency": "immediate"
            })
        
        # Festival advisory
        if festival.get("active", False):
            advisories.append({
                "type": "festival_health",
                "priority": "moderate",
                "message": f"During {festival.get('name', 'festival')}: Stay hydrated, avoid crowded areas if unwell, keep emergency contacts handy.",
                "target_audience": "all",
                "urgency": "advance"
            })
        
        # Calculate reach and engagement
        registered_users = 15247
        alerts_sent = len(advisories) * registered_users
        
        # Simulate engagement metrics
        open_rate = random.randint(75, 92)
        response_rate = random.randint(15, 28)
        satisfaction_score = random.randint(82, 94)
        
        # Channel distribution
        channel_distribution = {
            "WhatsApp": int(alerts_sent * 0.45),
            "SMS": int(alerts_sent * 0.30),
            "Mobile App": int(alerts_sent * 0.15),
            "Email": int(alerts_sent * 0.08),
            "Voice Call": int(alerts_sent * 0.02)
        }
        
        # Language distribution (based on Nagpur, Maharashtra demographics)
        language_distribution = {
            "Marathi": 45,
            "Hindi": 40,
            "English": 12,
            "Others": 3
        }
        
        # Generate alerts
        alerts = []
        if aqi > 300 or outbreak_risk == "high":
            alerts.append({
                "level": AlertLevel.HIGH.value,
                "message": "Critical health advisory active - mass communication in progress",
                "action_required": False
            })
        
        # Recommendations
        recommendations = []
        if open_rate < 80:
            recommendations.append("Improve message clarity and timing")
        if surge_activated:
            recommendations.append("Send follow-up advisory about telemedicine options")
        recommendations.append("Schedule preventive health webinar in local languages")
        
        # Advisory distribution plan
        distribution_plan = {
            "immediate": [a for a in advisories if a["urgency"] == "immediate"],
            "today": [a for a in advisories if a["urgency"] == "today"],
            "scheduled": [a for a in advisories if a["urgency"] == "advance"]
        }
        
        return {
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "predictions": {
                "active_advisories": len(advisories),
                "advisories": advisories,
                "registered_users": registered_users,
                "alerts_sent": alerts_sent,
                "channel_distribution": channel_distribution,
                "language_distribution": language_distribution,
                "engagement_metrics": {
                    "open_rate": open_rate,
                    "response_rate": response_rate,
                    "satisfaction_score": satisfaction_score
                },
                "distribution_plan": {
                    "immediate_alerts": len(distribution_plan["immediate"]),
                    "today_alerts": len(distribution_plan["today"]),
                    "scheduled_alerts": len(distribution_plan["scheduled"])
                },
                "communication_status": "Active",
                "multilingual_support": len(self.languages)
            },
            "confidence": 0.90,
            "alerts": alerts,
            "recommendations": recommendations
        }


# ==================== COMPLETE COORDINATOR WITH ALL 10 AGENTS ====================

class CompleteMultiAgentSystem:
    """Complete system with all 10 specialized agents"""
    
    def __init__(self):
        self.agents = {
            "forecasting": None,  # Import from main file
            "staff": None,
            "inventory": None,
            "equipment": None,
            "outbreak": None,
            "telemedicine": TelemedicineAgent(),
            "emergency": EmergencyAgent(),
            "coordination": CoordinationAgent(),
            "supply_chain": SupplyChainAgent(),
            "community": CommunityHealthAgent()
        }
    
    def run_complete_simulation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete simulation with all 10 agents"""
        results = {}
        
        # Agents 6-10 (new agents)
        telemedicine_result = self.agents["telemedicine"].process(input_data)
        results["telemedicine"] = telemedicine_result
        
        emergency_data = {
            **input_data,
            "severe_cases": telemedicine_result["predictions"]["severe_cases"]
        }
        emergency_result = self.agents["emergency"].process(emergency_data)
        results["emergency"] = emergency_result
        
        coordination_data = {
            **input_data,
            "surge_activated": emergency_result["predictions"]["surge_activated"]
        }
        coordination_result = self.agents["coordination"].process(coordination_data)
        results["coordination"] = coordination_result
        
        supply_chain_result = self.agents["supply_chain"].process(input_data)
        results["supply_chain"] = supply_chain_result
        
        community_data = {
            **input_data,
            "surge_activated": emergency_result["predictions"]["surge_activated"]
        }
        community_result = self.agents["community"].process(community_data)
        results["community"] = community_result
        
        return {
            "timestamp": datetime.now().isoformat(),
            "agents_6_to_10": results,
            "system_status": "All agents operational"
        }


# ==================== TEST EXECUTION ====================

if __name__ == "__main__":
    print("=" * 80)
    print("MEDINTEL - EXTENDED AGENTS (6-10) TEST")
    print("=" * 80)
    
    # Sample data
    test_data = {
        "predicted_inflow": 165,
        "aqi": 320,
        "outbreak_risk": "high",
        "festival": {"active": True, "name": "Diwali", "type": "major"},
        "er_capacity": 50,
        "surge_activated": True,
        "inventory_alerts": []
    }
    
    # Initialize system
    system = CompleteMultiAgentSystem()
    
    # Run simulation
    results = system.run_complete_simulation(test_data)
    
    # Display results
    for agent_name, agent_result in results["agents_6_to_10"].items():
        print(f"\n{'='*80}")
        print(f"🤖 {agent_result['agent_name'].upper()}")
        print(f"{'='*80}")
        print(f"Confidence: {agent_result['confidence']*100:.1f}%")
        
        print(f"\n📈 Key Predictions:")
        predictions = agent_result['predictions']
        for key, value in predictions.items():
            if isinstance(value, (int, float, str, bool)):
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        if agent_result['alerts']:
            print(f"\n⚠️  Alerts ({len(agent_result['alerts'])}):")
            for alert in agent_result['alerts']:
                print(f"  [{alert['level'].upper()}] {alert['message']}")
        
        if agent_result['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in agent_result['recommendations'][:3]:  # Show top 3
                print(f"  • {rec}")
    
    print("\n" + "=" * 80)
    print("✅ All Extended Agents (6-10) Operational")
    print("=" * 80)