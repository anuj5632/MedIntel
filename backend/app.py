"""MedIntel Platform Backend - Flask Gateway

Integrates all 5 AI agents into a unified REST API:
- Equipment Utility (predictive maintenance)
- Forecasting Agent (demand prediction)
- Inventory Management (supply optimization)
- Staff Optimization (scheduling)
- Triage Agent (patient emergency assessment)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import importlib.util
from datetime import datetime, timedelta
import traceback
import logging
import random
import math

# Add agents to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Agents'))

# Import agent modules
try:
    from equipment_utility.app.service import PredictionService
    from equipment_utility.app.models import SensorReading
except ImportError as e:
    logging.warning(f"Equipment utility agent not available: {e}")
    PredictionService = None
    SensorReading = None

try:
    from InventoryManagement.medical_inventory_agent import MedicalSupplyInventoryAgent
except ImportError as e:
    logging.warning(f"Inventory management agent not available: {e}")
    MedicalSupplyInventoryAgent = None

try:
    from staff_optimization.Staff_optimization import optimize_staff_schedule, Staff
except ImportError as e:
    logging.warning(f"Staff optimization agent not available: {e}")
    optimize_staff_schedule = None
    Staff = None

try:
    from triage_agent.triage_agent import assess_patient
except ImportError as e:
    logging.warning(f"Triage agent not available: {e}")
    assess_patient = None

try:
    from Predictive_Outbreak_Agent.predictive_outbreak import PredictiveOutbreakAgent
except ImportError as e:
    logging.warning(f"Predictive outbreak agent not available: {e}")
    PredictiveOutbreakAgent = None

try:
    # Import with folder name containing space
    import importlib.util
    spec = importlib.util.spec_from_file_location("supply_agent", r"C:\nextycce\MEDINTEL\Agents\SUPPLY CHAIN RESILLIENCE AGENT\supply_agent.py")
    supply_agent_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(supply_agent_module)
    SupplyChainResilienceAgent = supply_agent_module.SupplyChainResilienceAgent
    SupplyChainResilienceTrainer = supply_agent_module.SupplyChainResilienceTrainer
    logging.info("Supply chain resilience agent loaded successfully")
except Exception as e:
    logging.error(f"Supply chain resilience agent not available: {e}", exc_info=True)
    SupplyChainResilienceAgent = None
    SupplyChainResilienceTrainer = None

try:
    # Import Community Health Agent - add parent directory to path to resolve package imports
    agents_path = r"C:\nextycce\MEDINTEL\Agents"
    if agents_path not in sys.path:
        sys.path.insert(0, agents_path)
    
    from community_health_agent import CommunityHealthAgent
    logging.info("Community health agent loaded successfully")
except Exception as e:
    logging.error(f"Community health agent not available: {e}", exc_info=True)
    CommunityHealthAgent = None

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configure logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure app
app.config['SECRET_KEY'] = 'medintel-hospital-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medintel_hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
try:
    from models import db, init_db, User, UserRole
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        admin = User.query.filter_by(email='admin@medintel.com').first()
        if not admin:
            admin = User(
                email='admin@medintel.com',
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("Default admin user created: admin@medintel.com / admin123")
        logger.info("Database initialized successfully")
        
        # Initialize sample data
        init_db(app)
except Exception as e:
    logger.error(f"Database initialization error: {e}")

# Register authentication blueprint
try:
    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    logger.info("Auth blueprint registered")
except Exception as e:
    logger.error(f"Failed to register auth blueprint: {e}")

# Register hospital management blueprints
try:
    from routes import get_all_blueprints
    for name, blueprint, prefix in get_all_blueprints():
        app.register_blueprint(blueprint, url_prefix=prefix)
        logger.info(f"Registered blueprint: {name} at {prefix}")
except Exception as e:
    logger.error(f"Failed to register hospital management blueprints: {e}")

# Global agent instances
equipment_service = None
inventory_agent = None

# Initialize agents
def init_agents():
    global equipment_service, inventory_agent
    
    # Initialize equipment utility service
    if PredictionService:
        try:
            equipment_service = PredictionService()
            logger.info("Equipment utility service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize equipment service: {e}")
    
    # Initialize inventory agent
    if MedicalSupplyInventoryAgent:
        try:
            inventory_agent = MedicalSupplyInventoryAgent()
            logger.info("Inventory management agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize inventory agent: {e}")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check with agent status"""
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agents': {
            'equipment_utility': equipment_service is not None,
            'inventory_management': inventory_agent is not None,
            'staff_optimization': optimize_staff_schedule is not None,
            'demand_forecasting': True,
            'triage_agent': assess_patient is not None,
            'predictive_outbreak': PredictiveOutbreakAgent is not None,
            'supply_chain_resilience': SupplyChainResilienceAgent is not None,
            'community_health': CommunityHealthAgent is not None
        }
    }
    return jsonify(status)

# Equipment Utility Agent Endpoints
@app.route('/api/equipment/predict', methods=['POST'])
def predict_equipment():
    """Predict equipment failure risk"""
    if not equipment_service:
        return jsonify({'error': 'Equipment utility service not available'}), 503
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['equipment_id', 'temperature', 'pressure']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create sensor reading
        sensor_reading = SensorReading(
            equipment_id=data['equipment_id'],
            temperature=float(data['temperature']),
            pressure=float(data['pressure']),
            vibration=data.get('vibration', 0.0)
        )
        
        # Get prediction
        prediction = equipment_service.predict(sensor_reading)
        
        # Generate recommendations based on anomaly score
        recommendations = []
        if prediction.is_failure_risk:
            recommendations.extend([
                "Schedule immediate maintenance inspection",
                "Monitor temperature and pressure closely",
                "Consider replacing worn components"
            ])
        elif prediction.anomaly_score > 0.3:
            recommendations.extend([
                "Monitor equipment closely",
                "Schedule routine maintenance"
            ])
        else:
            recommendations.append("Equipment operating normally")
        
        return jsonify({
            'equipment_id': prediction.equipment_id,
            'anomaly_score': prediction.anomaly_score,
            'is_anomaly': prediction.is_failure_risk,
            'calibrated_score': prediction.anomaly_score,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Equipment prediction error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Staff Optimization Agent Endpoints
@app.route('/api/staff/optimize', methods=['POST'])
def optimize_staff():
    """Optimize staff scheduling using real algorithm"""
    if not optimize_staff_schedule:
        return jsonify({'error': 'Staff optimization service not available'}), 503
    
    try:
        data = request.get_json()
        
        # Extract parameters from frontend
        department = data.get('department', 'General')
        shift_type = data.get('shift_type', '8-hour')
        staff_count = int(data.get('staff_count', 10))
        patient_load = int(data.get('patient_load', 20))
        specialty_required = data.get('specialty_required', 'nurse')
        
        # Determine shift hours based on shift_type
        if shift_type == '12-hour':
            shift_hours = 12
            total_hours = 24  # 12-hour shifts for 24-hour coverage
        else:  # '8-hour' default
            shift_hours = 8
            total_hours = 24  # 8-hour shifts for 24-hour coverage
        
        # Create demand array based on patient load (constant demand for simplicity)
        demand_per_hour = max(1, patient_load // 8)  # Distribute patient load across hours
        demand = [demand_per_hour] * total_hours
        
        # Create staff list based on parameters
        staff_list = []
        for i in range(staff_count):
            if specialty_required.lower() == 'nurse':
                cost = 300 + (i * 20)  # Nurses cost 300-400 per hour
                max_hours = min(shift_hours, 12)  # Max 12 hours per day
            elif specialty_required.lower() == 'doctor':
                cost = 800 + (i * 50)  # Doctors cost 800-1000 per hour  
                max_hours = min(shift_hours, 8)   # Max 8 hours per day
            else:
                cost = 250 + (i * 15)  # General staff cost 250-350 per hour
                max_hours = min(shift_hours, 10)  # Max 10 hours per day
            
            staff_list.append(Staff(
                id=f"{department}-{specialty_required}-{i+1:02d}",
                role=specialty_required.lower(),
                max_hours_per_day=max_hours,
                cost_per_hour=cost
            ))
        
        # Call the real optimization algorithm
        optimization_result = optimize_staff_schedule(demand, staff_list)
        
        # Transform the result to match frontend expectations
        schedule = optimization_result['schedule']
        per_hour = optimization_result['per_hour']
        kpis = optimization_result['kpis']
        
        # Calculate efficiency score based on coverage
        total_demand = sum(demand)
        total_assigned = sum(h['assigned'] for h in per_hour)
        efficiency_score = round(min(100, (total_assigned / total_demand) * 100), 1)
        
        # Calculate coverage percentage
        coverage_percentage = round(kpis['avg_coverage_ratio'] * 100, 1)
        
        # Generate recommendations based on KPIs
        recommendations = []
        if kpis['understaffed_hours'] > 0:
            recommendations.append(f"Address {kpis['understaffed_hours']} understaffed hours")
        if kpis['max_understaffing'] > 2:
            recommendations.append(f"Reduce maximum understaffing from {kpis['max_understaffing']} staff")
        if coverage_percentage < 90:
            recommendations.append("Increase staff count to improve coverage")
        else:
            recommendations.append("Current staffing provides good coverage")
        
        if kpis['fairness_score'] < 0.8:
            recommendations.append("Improve workload distribution among staff")
        
        result = {
            'optimal_schedule': schedule,
            'per_hour_analysis': per_hour,
            'efficiency_score': efficiency_score,
            'coverage_percentage': coverage_percentage,
            'recommendations': recommendations,
            'cost_savings': round(kpis['total_cost'], 2),
            'kpis': kpis
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Staff optimization error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Inventory Management Agent Endpoints
@app.route('/api/inventory/forecast', methods=['POST'])
def forecast_inventory():
    """Forecast inventory demand"""
    if not inventory_agent:
        return jsonify({'error': 'Inventory management service not available'}), 503
    
    try:
        data = request.get_json()
        
        # Extract parameters from frontend
        item_id = data.get('item_id', 'unknown')
        category = data.get('category', 'General')
        current_stock = data.get('current_stock', 100)
        lead_time_days = data.get('lead_time_days', 7)
        seasonality = data.get('seasonality')
        
        # Generate forecast data
        from datetime import datetime, timedelta
        import random
        import math
        
        random.seed(hash(item_id) % 1000)  # Consistent results per item
        
        # Generate 14 days of forecast data
        forecast_data = []
        base_demand = 25 + random.randint(5, 35)
        
        for i in range(14):
            # Add seasonality effect
            seasonal_factor = 1.0
            if seasonality == 'weekly':
                seasonal_factor = 0.8 + 0.4 * math.sin(i * math.pi / 3.5)  # Weekly pattern
            elif seasonality == 'monthly':
                seasonal_factor = 0.9 + 0.2 * math.sin(i * math.pi / 15)  # Monthly pattern
            
            # Add random variation
            daily_demand = base_demand * seasonal_factor * (0.8 + 0.4 * random.random())
            
            forecast_data.append({
                'date': (datetime.now().date() + timedelta(days=i)).isoformat(),
                'predicted_demand': max(1, int(daily_demand)),
                'confidence_interval': [max(1, int(daily_demand * 0.8)), int(daily_demand * 1.2)]
            })
        
        # Calculate reorder point and safety stock
        avg_daily_demand = base_demand
        reorder_point = int(avg_daily_demand * lead_time_days * 1.5)  # 1.5x safety factor
        safety_stock = int(avg_daily_demand * lead_time_days * 0.5)
        
        # Generate recommendations
        recommendations = []
        if current_stock < safety_stock:
            recommendations.append(f"CRITICAL: Stock below safety level ({safety_stock} units)")
            recommendations.append("Place emergency order immediately")
        elif current_stock < reorder_point:
            recommendations.append(f"Stock approaching reorder point ({reorder_point} units)")
            recommendations.append("Schedule regular replenishment order")
        else:
            recommendations.append("Stock levels are adequate")
        
        if seasonality:
            recommendations.append(f"Consider {seasonality} patterns in ordering")
        
        if category == 'Medications':
            recommendations.append("Monitor expiration dates closely")
        elif category == 'PPE':
            recommendations.append("Ensure compliance with safety standards")
        
        result = {
            'item_id': item_id,
            'forecast_data': forecast_data,
            'reorder_point': reorder_point,
            'safety_stock': safety_stock,
            'recommendations': recommendations
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Inventory forecast error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Forecasting Agent Endpoints (placeholder)
@app.route('/api/forecast/demand', methods=['POST'])
def forecast_demand():
    """Forecast hospital demand"""
    try:
        data = request.get_json()
        
        # Extract parameters from frontend
        department = data.get('department')
        forecast_days = data.get('forecast_days', 30)
        historical_months = data.get('historical_months', 12)
        patient_type = data.get('patient_type')
        include_seasonality = data.get('include_seasonality', True)
        
        # Generate demand forecast
        from datetime import datetime, timedelta
        import random
        import math
        
        # Seed based on department for consistency
        random.seed(hash(str(department)) % 1000 if department else 42)
        
        # Base demand varies by department
        base_demands = {
            'Emergency': 45,
            'ICU': 25,
            'Surgery': 15,
            'Outpatient': 120,
            'Cardiology': 30,
            'Pediatrics': 35,
            'Oncology': 20,
            'Radiology': 60,
            'Laboratory': 80,
            'General': 50
        }
        
        base_demand = base_demands.get(department, 50)
        
        # Adjust for patient type
        if patient_type == 'Emergency':
            base_demand *= 1.2
        elif patient_type == 'Critical Care':
            base_demand *= 0.8
        elif patient_type == 'Outpatient':
            base_demand *= 1.5
        
        forecast_data = []
        peak_periods = []
        
        for i in range(forecast_days):
            # Seasonal factors
            seasonal_factor = 1.0
            if include_seasonality:
                # Weekly pattern (higher on weekdays)
                day_of_week = i % 7
                if day_of_week < 5:  # Weekdays
                    seasonal_factor *= 1.2
                else:  # Weekends
                    seasonal_factor *= 0.8
                
                # Monthly pattern
                seasonal_factor *= (0.9 + 0.2 * math.sin(i * math.pi / 15))
            
            # Random variation
            daily_demand = base_demand * seasonal_factor * (0.7 + 0.6 * random.random())
            predicted_demand = max(5, int(daily_demand))
            
            date_str = (datetime.now().date() + timedelta(days=i)).isoformat()
            forecast_data.append({
                'date': date_str,
                'predicted_demand': predicted_demand,
                'confidence_interval': [int(predicted_demand * 0.8), int(predicted_demand * 1.3)],
                'department': department
            })
            
            # Identify peak periods (above 120% of base)
            if predicted_demand > base_demand * 1.2:
                peak_periods.append({
                    'period': f'Day {i + 1} ({date_str})',
                    'estimated_demand': predicted_demand
                })
        
        # Generate capacity recommendations
        avg_demand = sum(item['predicted_demand'] for item in forecast_data) / len(forecast_data)
        max_demand = max(item['predicted_demand'] for item in forecast_data)
        
        recommendations = []
        if max_demand > avg_demand * 1.5:
            recommendations.append("Consider increasing staff capacity during peak periods")
        if len(peak_periods) > forecast_days * 0.2:
            recommendations.append("High variability detected - implement flexible scheduling")
        if department == 'Emergency':
            recommendations.append("Maintain 24/7 coverage with surge capacity planning")
        elif department == 'Surgery':
            recommendations.append("Optimize OR scheduling to match demand patterns")
        else:
            recommendations.append(f"Adjust {department} capacity based on predicted demand")
        
        if patient_type:
            recommendations.append(f"Special consideration for {patient_type} patient flow")
        
        result = {
            'forecast_period': f"{forecast_days} days",
            'forecast_data': forecast_data,
            'peak_periods': peak_periods,
            'capacity_recommendations': recommendations,
            'seasonality_factors': {
                'include_seasonality': include_seasonality,
                'weekly_pattern': True if include_seasonality else False,
                'monthly_pattern': True if include_seasonality else False
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Demand forecast error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Triage Agent Endpoints
@app.route('/api/triage/assess', methods=['POST'])
def assess_triage():
    """Assess patient priority and triage level using the actual triage agent"""
    try:
        data = request.get_json()
        
        if assess_patient is None:
            # Fallback to basic assessment if agent not available
            return jsonify({
                'error': 'Triage agent not available',
                'patient_id': data.get('patient_id', 'Unknown'),
                'triage_category': 'EMERGENCY',
                'urgency_score': 1.0,
                'message': 'Manual assessment required'
            }), 503
        
        # Normalize symptoms: frontend may send list; agent expects string
        raw_symptoms = data.get('symptoms', '')
        if isinstance(raw_symptoms, list):
            symptoms_str = ', '.join(str(s) for s in raw_symptoms)
            symptoms_list_for_frontend = raw_symptoms
        else:
            symptoms_str = str(raw_symptoms)
            symptoms_list_for_frontend = [
                s.strip() for s in symptoms_str.split(',') if s.strip()
            ]

        # Extract and prepare patient data for the triage agent
        patient_data = {
            'patient_id': data.get('patient_id', f'PAT-{int(datetime.now().timestamp())}'),
            'age': data.get('age', 50),
            'symptoms': symptoms_str,
            'medical_history': data.get('medical_history', []),
            'pain_score': data.get('pain_score', 5),
            'symptom_duration_days': data.get('symptom_duration_days', 1),
            'symptom_severity': data.get('symptom_severity', 2)
        }
        
        # Extract vitals from the request
        vitals = data.get('vitals', {})
        patient_data.update({
            'temperature': float(vitals.get('temperature', 98.6)),
            'heart_rate': int(vitals.get('heart_rate', 80)),
            'respiratory_rate': int(vitals.get('respiratory_rate', 16)),
            'spo2': int(vitals.get('oxygen_saturation', 98))
        })
        
        # Parse blood pressure
        bp_str = vitals.get('blood_pressure', '120/80')
        try:
            bp_sys, bp_dia = bp_str.split('/')
            patient_data['systolic_bp'] = int(bp_sys)
            patient_data['diastolic_bp'] = int(bp_dia)
        except Exception:
            patient_data['systolic_bp'] = 120
            patient_data['diastolic_bp'] = 80
        
        # Call the actual triage agent
        result = assess_patient(patient_data)
        
        # Transform result to match frontend expectations
        transformed_result = {
            'patient_id': result['patient_id'],
            'priority_level': result['triage_category'],
            'urgency_score': result['urgency_score'],
            'symptoms': symptoms_list_for_frontend,
            'vitals': {
                'heart_rate': result['vital_signs'].get('heart_rate'),
                'blood_pressure': result['vital_signs'].get('blood_pressure'),
                'temperature': result['vital_signs'].get('temperature'),
                'respiratory_rate': result['vital_signs'].get('respiratory_rate')
            },
            'risk_assessment': f"Risk level: {result['triage_category']}",
            'recommended_department': result['recommended_department'],
            'recommendations': result['recommendations']
        }
        
        return jsonify(transformed_result)
        
    except Exception as e:
        logger.error(f"Triage assessment error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Predictive Outbreak Agent Endpoint
@app.route('/api/outbreak/assess', methods=['POST'])
def assess_outbreak():
    """Analyze disease outbreak risk based on case data"""
    try:
        if not PredictiveOutbreakAgent:
            return jsonify({'error': 'Predictive outbreak agent not available'}), 503
        
        data = request.json
        
        # Extract time-series data
        cases_data = data.get('cases_data', [])
        
        if not cases_data:
            return jsonify({'error': 'No case data provided'}), 400
        
        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(cases_data)
        
        # Ensure required columns exist
        if 'date' not in df.columns or 'cases' not in df.columns:
            return jsonify({'error': 'Data must include "date" and "cases" columns'}), 400
        
        # Initialize agent
        outbreak_agent = PredictiveOutbreakAgent(
            forecast_horizon=data.get('forecast_horizon', 7),
            window_days=data.get('window_days', 7),
            n_clusters=data.get('n_clusters', 3)
        )
        
        # Compute outbreak risk
        result = outbreak_agent.compute_outbreak_risk(df)
        
        # Ensure all values are JSON-serializable
        def make_serializable(obj):
            if isinstance(obj, (int, float, str, bool)):
                return obj
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [make_serializable(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy types
                return obj.item()
            else:
                return str(obj)
        
        result = make_serializable(result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Outbreak assessment error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Supply Chain Resilience Agent Endpoint
@app.route('/api/supply-chain/analyze', methods=['POST'])
def analyze_supply_chain():
    """Analyze vendor reliability and supply chain resilience"""
    try:
        if not SupplyChainResilienceAgent or not SupplyChainResilienceTrainer:
            return jsonify({'error': 'Supply chain resilience agent not available'}), 503
        
        data = request.json
        vendors = data.get('vendors', [])
        
        if not vendors or len(vendors) == 0:
            return jsonify({'error': 'No vendor data provided'}), 400
        
        # Train the resilience model
        trainer = SupplyChainResilienceTrainer()
        df_training = trainer.generate_dataset(n=800)
        delay_weight, reliability_weight = trainer.train(df_training)
        
        # Initialize agent with trained weights
        threshold = data.get('threshold', 40)
        agent = SupplyChainResilienceAgent(
            delay_weight=delay_weight,
            reliability_weight=reliability_weight,
            threshold=threshold
        )
        
        # Run analysis on vendors
        result_df = agent.run(vendors)
        
        # Convert to JSON-serializable format
        results = result_df.to_dict(orient='records')
        
        # Calculate overall metrics
        overall_score = result_df['score'].mean()
        switch_count = len(result_df[result_df['recommendation'] == 'SWITCH_VENDOR'])
        
        response = {
            'vendors': results,
            'overall_resilience_score': float(overall_score),
            'vendors_to_switch': switch_count,
            'total_vendors': len(vendors),
            'weights': {
                'delay_weight': float(delay_weight),
                'reliability_weight': float(reliability_weight)
            },
            'threshold': float(threshold),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Supply chain analysis error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Community Health Agent Endpoint
@app.route('/api/community-health/assess', methods=['POST'])
def assess_community_health():
    """Generate public health advisory for community"""
    try:
        if not CommunityHealthAgent:
            return jsonify({'error': 'Community health agent not available'}), 503
        
        data = request.get_json()
        
        # Validate required fields
        if 'location_name' not in data:
            return jsonify({'error': 'Missing required field: location_name'}), 400
        
        # Initialize agent
        agent = CommunityHealthAgent()
        
        # Prepare context with all provided data
        context = {
            'location_name': data.get('location_name', 'Unknown Location'),
            'languages': data.get('languages', ['en']),
            'pollution_aqi': data.get('pollution_aqi'),
            'resp_case_trend': data.get('resp_case_trend'),
            'outbreak_risk': data.get('outbreak_risk'),
            'outbreak_type': data.get('outbreak_type'),
            'heat_index': data.get('heat_index'),
            'flood_risk': data.get('flood_risk'),
            'notes': data.get('notes')
        }
        
        # Generate advisory
        result = agent.generate_advisory(context)
        
        # Get primary language for field translations
        primary_lang = context['languages'][0] if context['languages'] else 'en'
        
        # Translation dictionaries for UI field names
        field_translations = {
            'en': {
                'severity': 'Severity',
                'risk_factors': 'Risk Factors',
                'recommended_channels': 'Recommended Communication Channels',
                'public_health_messages': 'Public Health Messages',
            },
            'hi': {
                'severity': 'गंभीरता',
                'risk_factors': 'जोखिम कारक',
                'recommended_channels': 'अनुशंसित संचार चैनल',
                'public_health_messages': 'सार्वजनिक स्वास्थ्य संदेश',
            },
            'es': {
                'severity': 'Severidad',
                'risk_factors': 'Factores de Riesgo',
                'recommended_channels': 'Canales de Comunicación Recomendados',
                'public_health_messages': 'Mensajes de Salud Pública',
            },
            'fr': {
                'severity': 'Gravité',
                'risk_factors': 'Facteurs de Risque',
                'recommended_channels': 'Canaux de Communication Recommandés',
                'public_health_messages': 'Messages de Santé Publique',
            },
            'ta': {
                'severity': 'கடுமை',
                'risk_factors': 'ஆபத்து காரணிகள்',
                'recommended_channels': 'பரிந்துரைக்கப்பட்ட संचार சேனல்கள்',
                'public_health_messages': 'பொது சுகாதார செய்திகள்',
            }
        }
        
        trans = field_translations.get(primary_lang, field_translations['en'])
        
        # Add metadata and translated field names
        result['location'] = context['location_name']
        result['timestamp'] = datetime.now().isoformat()
        result['_field_names'] = trans  # Include translations for frontend
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Community health assessment error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Dashboard summary endpoint
@app.route('/api/dashboard/summary', methods=['GET'])
def dashboard_summary():
    """Get overall system status for dashboard"""
    try:
        summary = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'operational',
            'alerts': [
                {
                    'type': 'equipment',
                    'severity': 'medium',
                    'message': '2 devices showing elevated temperature'
                },
                {
                    'type': 'inventory',
                    'severity': 'low',
                    'message': 'Surgical gloves running low'
                }
            ],
            'quick_stats': {
                'equipment_monitored': 45,
                'staff_scheduled': 28,
                'inventory_items': 120,
                'active_forecasts': 3
            }
        }
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Dashboard summary error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_agents()
    app.run(debug=False, host='0.0.0.0', port=5000)