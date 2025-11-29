"""
Routes Package for MedIntel Hospital Management System
Blueprints for all hospital management modules
"""

# Import all blueprints - they will be registered in app.py
# Each blueprint handles a specific module

def get_all_blueprints():
    """
    Return all available blueprints.
    Import lazily to avoid circular dependencies.
    """
    blueprints = []
    
    try:
        from .patients import patients_bp
        blueprints.append(('patients', patients_bp, '/api/patients'))
    except ImportError as e:
        print(f"Warning: Could not import patients blueprint: {e}")
    
    try:
        from .appointments import appointments_bp
        blueprints.append(('appointments', appointments_bp, '/api/appointments'))
    except ImportError as e:
        print(f"Warning: Could not import appointments blueprint: {e}")
    
    try:
        from .billing import billing_bp
        blueprints.append(('billing', billing_bp, '/api/billing'))
    except ImportError as e:
        print(f"Warning: Could not import billing blueprint: {e}")
    
    try:
        from .pharmacy import pharmacy_bp
        blueprints.append(('pharmacy', pharmacy_bp, '/api/pharmacy'))
    except ImportError as e:
        print(f"Warning: Could not import pharmacy blueprint: {e}")
    
    try:
        from .lab import lab_bp
        blueprints.append(('lab', lab_bp, '/api/lab'))
    except ImportError as e:
        print(f"Warning: Could not import lab blueprint: {e}")
    
    try:
        from .ipd import ipd_bp
        blueprints.append(('ipd', ipd_bp, '/api/ipd'))
    except ImportError as e:
        print(f"Warning: Could not import ipd blueprint: {e}")
    
    try:
        from .inventory import inventory_bp
        blueprints.append(('inventory', inventory_bp, '/api/inventory'))
    except ImportError as e:
        print(f"Warning: Could not import inventory blueprint: {e}")
    
    try:
        from .reports import reports_bp
        blueprints.append(('reports', reports_bp, '/api/reports'))
    except ImportError as e:
        print(f"Warning: Could not import reports blueprint: {e}")
    
    try:
        from .ai_integration import ai_bp
        blueprints.append(('ai', ai_bp, '/api/ai'))
    except ImportError as e:
        print(f"Warning: Could not import ai blueprint: {e}")
    
    return blueprints
