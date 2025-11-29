"""
AI Agent Integration Module for MedIntel Hospital Management System
Integrates all 8 AI agents with the hospital management system
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify
import sys
import os

# Add agents path
agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Agents')
sys.path.insert(0, agents_path)

from auth import token_required, role_required

ai_bp = Blueprint('ai', __name__)

# ============== TRIAGE AGENT ==============

@ai_bp.route('/triage/assess', methods=['POST'])
@token_required
@role_required('doctor', 'nurse', 'admin')
def triage_assessment():
    """Get AI-powered triage assessment for a patient"""
    try:
        data = request.get_json()
        
        # Import triage agent
        try:
            from triage_agent.triage_system import TriageSystem
            triage = TriageSystem()
            
            patient_data = {
                'symptoms': data.get('symptoms', []),
                'vitals': data.get('vitals', {}),
                'age': data.get('age'),
                'gender': data.get('gender'),
                'medical_history': data.get('medical_history', [])
            }
            
            assessment = triage.assess_patient(patient_data)
            
            return jsonify({
                'success': True,
                'assessment': assessment
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Triage agent not available',
                'details': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_triage_summary():
    """Get triage summary for dashboard"""
    try:
        from triage_agent.triage_system import TriageSystem
        triage = TriageSystem()
        return triage.get_summary()
    except:
        return None

# ============== COMMUNITY HEALTH AGENT ==============

@ai_bp.route('/community-health/analyze', methods=['POST'])
@token_required
def community_health_analysis():
    """Get community health analysis"""
    try:
        data = request.get_json()
        
        try:
            from community_health_agent.community_agent import CommunityHealthAgent
            agent = CommunityHealthAgent()
            
            analysis = agent.analyze(
                region=data.get('region'),
                metrics=data.get('metrics', {}),
                language=data.get('language', 'en')
            )
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Community Health agent not available',
                'details': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== PREDICTIVE OUTBREAK AGENT ==============

@ai_bp.route('/outbreak/predict', methods=['POST'])
@token_required
@role_required('doctor', 'admin')
def predict_outbreak():
    """Get outbreak predictions"""
    try:
        data = request.get_json()
        
        try:
            from Predictive_Outbreak_Agent.outbreak_predictor import OutbreakPredictor
            predictor = OutbreakPredictor()
            
            prediction = predictor.predict(
                region=data.get('region'),
                historical_data=data.get('historical_data', {}),
                current_cases=data.get('current_cases', [])
            )
            
            return jsonify({
                'success': True,
                'prediction': prediction
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Outbreak Prediction agent not available',
                'details': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_outbreak_prediction():
    """Get outbreak prediction for dashboard"""
    try:
        from Predictive_Outbreak_Agent.outbreak_predictor import OutbreakPredictor
        predictor = OutbreakPredictor()
        return predictor.get_current_alerts()
    except:
        return None

# ============== INVENTORY MANAGEMENT AGENT ==============

@ai_bp.route('/inventory-ai/optimize', methods=['POST'])
@token_required
@role_required('admin', 'inventory_manager')
def optimize_inventory():
    """Get AI-powered inventory optimization suggestions"""
    try:
        data = request.get_json()
        
        try:
            from InventoryManagement.inventory_optimizer import InventoryOptimizer
            optimizer = InventoryOptimizer()
            
            suggestions = optimizer.optimize(
                current_inventory=data.get('inventory', []),
                usage_history=data.get('usage_history', []),
                budget=data.get('budget')
            )
            
            return jsonify({
                'success': True,
                'suggestions': suggestions
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Inventory Management agent not available',
                'details': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== FORECASTING AGENT ==============

@ai_bp.route('/forecast', methods=['POST'])
@token_required
def get_forecast():
    """Get demand/supply forecasting"""
    try:
        data = request.get_json()
        
        try:
            from forecasting_agent.forecaster import Forecaster
            forecaster = Forecaster()
            
            forecast = forecaster.forecast(
                item_type=data.get('item_type'),
                historical_data=data.get('historical_data', []),
                forecast_days=data.get('days', 30)
            )
            
            return jsonify({
                'success': True,
                'forecast': forecast
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Forecasting agent not available',
                'details': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_inventory_forecast():
    """Get inventory forecast for dashboard"""
    try:
        from forecasting_agent.forecaster import Forecaster
        forecaster = Forecaster()
        return forecaster.get_critical_forecasts()
    except:
        return None

# ============== STAFF OPTIMIZATION AGENT ==============

@ai_bp.route('/staff/optimize', methods=['POST'])
@token_required
@role_required('admin')
def optimize_staff():
    """Get AI-powered staff scheduling optimization"""
    try:
        data = request.get_json()
        
        try:
            from staff_optimization.staff_optimizer import StaffOptimizer
            optimizer = StaffOptimizer()
            
            schedule = optimizer.optimize(
                staff_list=data.get('staff', []),
                shift_requirements=data.get('requirements', {}),
                constraints=data.get('constraints', {})
            )
            
            return jsonify({
                'success': True,
                'schedule': schedule
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Staff Optimization agent not available',
                'details': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_staff_recommendations():
    """Get staff recommendations for dashboard"""
    try:
        from staff_optimization.staff_optimizer import StaffOptimizer
        optimizer = StaffOptimizer()
        return optimizer.get_current_recommendations()
    except:
        return None

# ============== SUPPLY CHAIN RESILIENCE AGENT ==============

@ai_bp.route('/supply-chain/analyze', methods=['POST'])
@token_required
@role_required('admin', 'inventory_manager')
def analyze_supply_chain():
    """Get supply chain analysis and risk assessment"""
    try:
        data = request.get_json()
        
        try:
            # Note: folder name has space
            supply_chain_path = os.path.join(agents_path, 'SUPPLY CHAIN RESILLIENCE AGENT')
            sys.path.insert(0, supply_chain_path)
            
            from supply_chain_analyzer import SupplyChainAnalyzer
            analyzer = SupplyChainAnalyzer()
            
            analysis = analyzer.analyze(
                suppliers=data.get('suppliers', []),
                inventory=data.get('inventory', []),
                demand_forecast=data.get('demand_forecast', [])
            )
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Supply Chain agent not available',
                'details': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== EQUIPMENT UTILITY AGENT ==============

@ai_bp.route('/equipment/analyze', methods=['POST'])
@token_required
@role_required('admin', 'technician')
def analyze_equipment():
    """Get equipment utilization analysis and maintenance predictions"""
    try:
        data = request.get_json()
        
        try:
            from equipment_utility.equipment_analyzer import EquipmentAnalyzer
            analyzer = EquipmentAnalyzer()
            
            analysis = analyzer.analyze(
                equipment_list=data.get('equipment', []),
                usage_data=data.get('usage_data', []),
                maintenance_history=data.get('maintenance_history', [])
            )
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': 'Equipment Utility agent not available',
                'details': str(e)
            }), 503
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== UNIFIED AI DASHBOARD ==============

@ai_bp.route('/status', methods=['GET'])
@token_required
def ai_agents_status():
    """Get status of all AI agents"""
    agents_status = []
    
    # Check each agent
    agents_to_check = [
        ('Triage Agent', 'triage_agent.triage_system', 'TriageSystem'),
        ('Community Health Agent', 'community_health_agent.community_agent', 'CommunityHealthAgent'),
        ('Predictive Outbreak Agent', 'Predictive_Outbreak_Agent.outbreak_predictor', 'OutbreakPredictor'),
        ('Inventory Management Agent', 'InventoryManagement.inventory_optimizer', 'InventoryOptimizer'),
        ('Forecasting Agent', 'forecasting_agent.forecaster', 'Forecaster'),
        ('Staff Optimization Agent', 'staff_optimization.staff_optimizer', 'StaffOptimizer'),
        ('Equipment Utility Agent', 'equipment_utility.equipment_analyzer', 'EquipmentAnalyzer'),
    ]
    
    for name, module, class_name in agents_to_check:
        try:
            __import__(module)
            agents_status.append({
                'name': name,
                'status': 'available',
                'module': module
            })
        except ImportError:
            agents_status.append({
                'name': name,
                'status': 'unavailable',
                'module': module
            })
    
    # Special check for Supply Chain agent (different path)
    try:
        supply_chain_path = os.path.join(agents_path, 'SUPPLY CHAIN RESILLIENCE AGENT')
        sys.path.insert(0, supply_chain_path)
        from supply_chain_analyzer import SupplyChainAnalyzer
        agents_status.append({
            'name': 'Supply Chain Resilience Agent',
            'status': 'available',
            'module': 'supply_chain_analyzer'
        })
    except ImportError:
        agents_status.append({
            'name': 'Supply Chain Resilience Agent',
            'status': 'unavailable',
            'module': 'supply_chain_analyzer'
        })
    
    available_count = sum(1 for a in agents_status if a['status'] == 'available')
    
    return jsonify({
        'agents': agents_status,
        'total': len(agents_status),
        'available': available_count,
        'unavailable': len(agents_status) - available_count
    })

@ai_bp.route('/run-all', methods=['POST'])
@token_required
@role_required('admin')
def run_all_agents():
    """Run all AI agents and get consolidated insights"""
    try:
        data = request.get_json() or {}
        results = {}
        
        # Run each agent and collect results
        # Triage
        try:
            from triage_agent.triage_system import TriageSystem
            triage = TriageSystem()
            results['triage'] = {'status': 'success', 'data': triage.get_summary()}
        except Exception as e:
            results['triage'] = {'status': 'error', 'error': str(e)}
        
        # Community Health
        try:
            from community_health_agent.community_agent import CommunityHealthAgent
            agent = CommunityHealthAgent()
            results['community_health'] = {'status': 'success', 'data': agent.get_summary()}
        except Exception as e:
            results['community_health'] = {'status': 'error', 'error': str(e)}
        
        # Outbreak
        try:
            from Predictive_Outbreak_Agent.outbreak_predictor import OutbreakPredictor
            predictor = OutbreakPredictor()
            results['outbreak'] = {'status': 'success', 'data': predictor.get_current_alerts()}
        except Exception as e:
            results['outbreak'] = {'status': 'error', 'error': str(e)}
        
        # Forecasting
        try:
            from forecasting_agent.forecaster import Forecaster
            forecaster = Forecaster()
            results['forecasting'] = {'status': 'success', 'data': forecaster.get_critical_forecasts()}
        except Exception as e:
            results['forecasting'] = {'status': 'error', 'error': str(e)}
        
        # Staff Optimization
        try:
            from staff_optimization.staff_optimizer import StaffOptimizer
            optimizer = StaffOptimizer()
            results['staff_optimization'] = {'status': 'success', 'data': optimizer.get_current_recommendations()}
        except Exception as e:
            results['staff_optimization'] = {'status': 'error', 'error': str(e)}
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
