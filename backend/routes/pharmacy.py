"""
Pharmacy Module for MedIntel Hospital Management System
Medicine inventory, prescriptions, dispensing
"""

from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify
from models import (
    db, Medicine, Prescription, PrescriptionItem, Patient,
    generate_id
)
from auth import token_required, role_required, log_action

pharmacy_bp = Blueprint('pharmacy', __name__)

# ============== MEDICINES ==============

@pharmacy_bp.route('/medicines', methods=['GET'])
@token_required
def list_medicines():
    """List all medicines with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category')
        low_stock = request.args.get('low_stock', type=bool)
        
        query = Medicine.query.filter_by(is_active=True)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Medicine.name.ilike(search_filter),
                    Medicine.generic_name.ilike(search_filter),
                    Medicine.brand.ilike(search_filter)
                )
            )
        
        if category:
            query = query.filter(Medicine.category == category)
        
        if low_stock:
            query = query.filter(Medicine.quantity_in_stock <= Medicine.reorder_level)
        
        medicines = query.order_by(Medicine.name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'medicines': [m.to_dict() for m in medicines.items],
            'total': medicines.total,
            'pages': medicines.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pharmacy_bp.route('/medicines', methods=['POST'])
@token_required
@role_required('admin', 'pharmacist')
def add_medicine():
    """Add a new medicine"""
    try:
        data = request.get_json()
        
        medicine = Medicine(
            name=data['name'],
            generic_name=data.get('generic_name'),
            brand=data.get('brand'),
            category=data.get('category'),
            composition=data.get('composition'),
            strength=data.get('strength'),
            unit=data.get('unit'),
            manufacturer=data.get('manufacturer'),
            batch_number=data.get('batch_number'),
            mrp=data.get('mrp'),
            purchase_price=data.get('purchase_price'),
            selling_price=data.get('selling_price'),
            quantity_in_stock=data.get('quantity_in_stock', 0),
            reorder_level=data.get('reorder_level', 10),
            storage_location=data.get('storage_location'),
            requires_prescription=data.get('requires_prescription', True)
        )
        
        if data.get('expiry_date'):
            medicine.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        
        db.session.add(medicine)
        db.session.commit()
        
        log_action('medicine_added', 'medicine', medicine.id)
        
        return jsonify({
            'message': 'Medicine added successfully',
            'medicine': medicine.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pharmacy_bp.route('/medicines/<int:medicine_id>', methods=['PUT'])
@token_required
@role_required('admin', 'pharmacist')
def update_medicine(medicine_id):
    """Update medicine details"""
    try:
        medicine = Medicine.query.get_or_404(medicine_id)
        data = request.get_json()
        
        updateable = [
            'name', 'generic_name', 'brand', 'category', 'composition',
            'strength', 'unit', 'manufacturer', 'batch_number',
            'mrp', 'purchase_price', 'selling_price',
            'quantity_in_stock', 'reorder_level', 'storage_location',
            'requires_prescription'
        ]
        
        for field in updateable:
            if field in data:
                setattr(medicine, field, data[field])
        
        if 'expiry_date' in data and data['expiry_date']:
            medicine.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        log_action('medicine_updated', 'medicine', medicine.id)
        
        return jsonify({
            'message': 'Medicine updated successfully',
            'medicine': medicine.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pharmacy_bp.route('/medicines/<int:medicine_id>/stock', methods=['POST'])
@token_required
@role_required('admin', 'pharmacist')
def update_stock(medicine_id):
    """Update medicine stock"""
    try:
        medicine = Medicine.query.get_or_404(medicine_id)
        data = request.get_json()
        
        adjustment = data.get('adjustment', 0)
        reason = data.get('reason', '')
        
        medicine.quantity_in_stock += adjustment
        
        if medicine.quantity_in_stock < 0:
            return jsonify({'error': 'Stock cannot be negative'}), 400
        
        db.session.commit()
        
        log_action('stock_updated', 'medicine', medicine.id, new_values={'adjustment': adjustment, 'reason': reason})
        
        return jsonify({
            'message': 'Stock updated successfully',
            'medicine': medicine.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== PRESCRIPTIONS ==============

@pharmacy_bp.route('/prescriptions', methods=['GET'])
@token_required
def list_prescriptions():
    """List prescriptions"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        patient_id = request.args.get('patient_id', type=int)
        dispensed = request.args.get('dispensed')
        
        query = Prescription.query
        
        if patient_id:
            query = query.filter(Prescription.patient_id == patient_id)
        
        if dispensed == 'true':
            query = query.filter(Prescription.is_dispensed == True)
        elif dispensed == 'false':
            query = query.filter(Prescription.is_dispensed == False)
        
        prescriptions = query.order_by(Prescription.prescription_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'prescriptions': [p.to_dict() for p in prescriptions.items],
            'total': prescriptions.total,
            'pages': prescriptions.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pharmacy_bp.route('/prescriptions', methods=['POST'])
@token_required
@role_required('doctor', 'admin')
def create_prescription():
    """Create a new prescription"""
    try:
        data = request.get_json()
        
        # Validate patient
        patient = Patient.query.get(data.get('patient_id'))
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        prescription_id = generate_id('RX', Prescription)
        
        prescription = Prescription(
            prescription_id=prescription_id,
            patient_id=data['patient_id'],
            doctor_id=request.current_user.id,
            appointment_id=data.get('appointment_id'),
            medical_record_id=data.get('medical_record_id'),
            diagnosis=data.get('diagnosis'),
            notes=data.get('notes')
        )
        
        db.session.add(prescription)
        db.session.flush()
        
        # Add prescription items
        for item_data in data.get('items', []):
            item = PrescriptionItem(
                prescription_id=prescription.id,
                medicine_id=item_data.get('medicine_id'),
                medicine_name=item_data['medicine_name'],
                dosage=item_data.get('dosage'),
                frequency=item_data.get('frequency'),
                duration=item_data.get('duration'),
                quantity=item_data.get('quantity'),
                instructions=item_data.get('instructions')
            )
            db.session.add(item)
        
        db.session.commit()
        
        log_action('prescription_created', 'prescription', prescription.id)
        
        return jsonify({
            'message': 'Prescription created successfully',
            'prescription': prescription.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pharmacy_bp.route('/prescriptions/<int:prescription_id>/dispense', methods=['POST'])
@token_required
@role_required('pharmacist', 'admin')
def dispense_prescription(prescription_id):
    """Dispense prescription medicines"""
    try:
        prescription = Prescription.query.get_or_404(prescription_id)
        data = request.get_json() or {}
        
        if prescription.is_dispensed:
            return jsonify({'error': 'Prescription already dispensed'}), 400
        
        # Update stock for each item
        for item in prescription.items:
            if item.medicine_id:
                medicine = Medicine.query.get(item.medicine_id)
                if medicine:
                    if medicine.quantity_in_stock < (item.quantity or 0):
                        return jsonify({
                            'error': f'Insufficient stock for {medicine.name}'
                        }), 400
                    medicine.quantity_in_stock -= (item.quantity or 0)
            item.is_dispensed = True
        
        prescription.is_dispensed = True
        prescription.dispensed_at = datetime.utcnow()
        prescription.dispensed_by = request.current_user.id
        
        db.session.commit()
        
        log_action('prescription_dispensed', 'prescription', prescription.id)
        
        return jsonify({
            'message': 'Prescription dispensed successfully',
            'prescription': prescription.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== PHARMACY STATISTICS ==============

@pharmacy_bp.route('/stats', methods=['GET'])
@token_required
def pharmacy_statistics():
    """Get pharmacy statistics"""
    try:
        # Low stock medicines
        low_stock = Medicine.query.filter(
            Medicine.is_active == True,
            Medicine.quantity_in_stock <= Medicine.reorder_level
        ).count()
        
        # Expiring soon (within 30 days)
        expiry_threshold = date.today() + timedelta(days=30)
        expiring_soon = Medicine.query.filter(
            Medicine.is_active == True,
            Medicine.expiry_date <= expiry_threshold,
            Medicine.expiry_date > date.today()
        ).count()
        
        # Expired
        expired = Medicine.query.filter(
            Medicine.is_active == True,
            Medicine.expiry_date <= date.today()
        ).count()
        
        # Total medicines
        total_medicines = Medicine.query.filter_by(is_active=True).count()
        
        # Pending prescriptions
        pending_prescriptions = Prescription.query.filter_by(is_dispensed=False).count()
        
        # Today's dispensed
        today = date.today()
        today_dispensed = Prescription.query.filter(
            Prescription.is_dispensed == True,
            db.func.date(Prescription.dispensed_at) == today
        ).count()
        
        return jsonify({
            'total_medicines': total_medicines,
            'low_stock': low_stock,
            'expiring_soon': expiring_soon,
            'expired': expired,
            'pending_prescriptions': pending_prescriptions,
            'today_dispensed': today_dispensed
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pharmacy_bp.route('/low-stock', methods=['GET'])
@token_required
def get_low_stock():
    """Get low stock medicines"""
    try:
        medicines = Medicine.query.filter(
            Medicine.is_active == True,
            Medicine.quantity_in_stock <= Medicine.reorder_level
        ).all()
        
        return jsonify({
            'medicines': [m.to_dict() for m in medicines]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pharmacy_bp.route('/expiring', methods=['GET'])
@token_required
def get_expiring():
    """Get expiring medicines"""
    try:
        days = request.args.get('days', 30, type=int)
        expiry_threshold = date.today() + timedelta(days=days)
        
        medicines = Medicine.query.filter(
            Medicine.is_active == True,
            Medicine.expiry_date <= expiry_threshold,
            Medicine.expiry_date > date.today()
        ).order_by(Medicine.expiry_date).all()
        
        return jsonify({
            'medicines': [m.to_dict() for m in medicines]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
