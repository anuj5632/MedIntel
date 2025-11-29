"""
MedIntel Platform API - Flask Backend
Integrates all 4 agents into a unified REST API for the React frontend.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from pathlib import Path
import logging

# Add the project root to the path so we can import from agents
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import agent services
from agents.equipment_utility.app.service import PredictionService
from agents.equipment_utility.app.models import SensorReading
from agents.staff_optimization.Staff_optimization import optimize_staff_schedule, Staff
from Agents.InventoryManagement.medical_inventory_agent import MedicalSupplyInventoryAgent

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
equipment_service = None
inventory_agent = None

def initialize_services():
    """Initialize all agent services"""
    global equipment_service, inventory_agent
    try:
        # Equipment Utility Agent
        equipment_service = PredictionService()
        logger.info("Equipment Utility service initialized")
        
        # Inventory Management Agent
        inventory_agent = MedicalSupplyInventoryAgent()
        logger.info("Inventory Management agent initialized")
        
    except Exception as e:
        logger.error(f"Error initializing services: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'equipment_utility': equipment_service is not None,
            'inventory_management': inventory_agent is not None,
            'staff_optimization': True,  # Always available
            'forecasting': True  # Placeholder for now
        }
    })

@app.route('/api/equipment/predict', methods=['POST'])
def predict_equipment_failure():
    """Equipment failure prediction endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['equipment_id', 'temperature', 'pressure']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Create sensor reading
        sensor_reading = SensorReading(
            equipment_id=data['equipment_id'],
            temperature=data['temperature'],
            pressure=data['pressure'],
            vibration=data.get('vibration', 0.0)
        )
        
        # Get prediction
        prediction = equipment_service.predict(sensor_reading)
        
        return jsonify({
            'equipment_id': prediction.equipment_id,
            'anomaly_score': prediction.anomaly_score,
            'is_failure_risk': prediction.is_failure_risk,
            'maintenance_warning': prediction.maintenance_warning,
            'generated_at': prediction.generated_at.isoformat()
        })
        
    except Exception as e:
        logger.error(f"Equipment prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/optimize', methods=['POST'])
def optimize_staff():
    """Staff optimization endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if 'demand' not in data or 'staff' not in data:
            return jsonify({'error': 'Missing demand or staff data'}), 400
        
        # Parse staff data
        staff_list = []
        for staff_data in data['staff']:
            staff = Staff(
                id=staff_data['id'],
                role=staff_data['role'],
                max_hours_per_day=staff_data['max_hours_per_day'],
                cost_per_hour=staff_data['cost_per_hour']
            )
            staff_list.append(staff)
        
        # Optimize schedule
        result = optimize_staff_schedule(data['demand'], staff_list)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Staff optimization error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/forecast', methods=['POST'])
def forecast_inventory():
    """Inventory forecasting endpoint"""
    try:
        data = request.get_json()
        
        # This would need sample data or pre-trained model
        # For now, return a placeholder response
        return jsonify({
            'message': 'Inventory forecasting not yet implemented',
            'item_id': data.get('item_id', 'unknown'),
            'forecast': [10, 12, 8, 15, 11, 9, 13]  # Placeholder 7-day forecast
        })
        
    except Exception as e:
        logger.error(f"Inventory forecast error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecasting/demand', methods=['POST'])
def forecast_demand():
    """Hospital demand forecasting endpoint"""
    try:
        data = request.get_json()
        
        # This would integrate with the forecasting agent
        # For now, return a placeholder response
        return jsonify({
            'hospital_id': data.get('hospital_id', 'unknown'),
            'start_date': data.get('start_date'),
            'forecast': [
                {'date': '2025-11-28', 'predicted_demand': 85, 'confidence': 0.92},
                {'date': '2025-11-29', 'predicted_demand': 92, 'confidence': 0.89},
                {'date': '2025-11-30', 'predicted_demand': 78, 'confidence': 0.91}
            ]
        })
        
    except Exception as e:
        logger.error(f"Demand forecast error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    initialize_services()
    app.run(debug=True, host='0.0.0.0', port=5000)