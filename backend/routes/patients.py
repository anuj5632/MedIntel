"""
Patient Management Module for MedIntel Hospital Management System
Patient registration, EMR, medical records, vitals
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify
from models import (
    db, Patient, VitalSigns, MedicalRecord, 
    generate_id, Gender
)
from auth import token_required, role_required, log_action

patients_bp = Blueprint('patients', __name__)

# ============== PATIENT REGISTRATION ==============

@patients_bp.route('', methods=['GET'])
@token_required
def list_patients():
    """List all patients with pagination and search"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Patient.query.filter_by(is_active=True)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Patient.first_name.ilike(search_filter),
                    Patient.last_name.ilike(search_filter),
                    Patient.patient_id.ilike(search_filter),
                    Patient.phone.ilike(search_filter),
                    Patient.email.ilike(search_filter)
                )
            )
        
        patients = query.order_by(Patient.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'patients': [p.to_dict() for p in patients.items],
            'total': patients.total,
            'pages': patients.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('', methods=['POST'])
@token_required
def create_patient():
    """Register a new patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['first_name', 'last_name', 'date_of_birth', 'gender', 'phone']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check for duplicate phone
        if Patient.query.filter_by(phone=data['phone'], is_active=True).first():
            return jsonify({'error': 'Patient with this phone number already exists'}), 400
        
        # Generate unique patient ID
        patient_id = generate_id('PAT', Patient)
        
        # Parse date of birth
        try:
            dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        patient = Patient(
            patient_id=patient_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=dob,
            gender=Gender(data['gender']),
            blood_group=data.get('blood_group'),
            phone=data['phone'],
            alternate_phone=data.get('alternate_phone'),
            email=data.get('email'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            pincode=data.get('pincode'),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            emergency_contact_relation=data.get('emergency_contact_relation'),
            insurance_provider=data.get('insurance_provider'),
            insurance_id=data.get('insurance_id'),
            allergies=data.get('allergies'),
            chronic_conditions=data.get('chronic_conditions')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        log_action('patient_registered', 'patient', patient.id)
        
        return jsonify({
            'message': 'Patient registered successfully',
            'patient': patient.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['GET'])
@token_required
def get_patient(patient_id):
    """Get patient details"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Get recent vitals
        recent_vitals = VitalSigns.query.filter_by(patient_id=patient_id)\
            .order_by(VitalSigns.recorded_at.desc()).first()
        
        # Get visit count
        visit_count = MedicalRecord.query.filter_by(patient_id=patient_id).count()
        
        patient_data = patient.to_dict()
        patient_data['recent_vitals'] = recent_vitals.to_dict() if recent_vitals else None
        patient_data['total_visits'] = visit_count
        
        return jsonify({'patient': patient_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
@token_required
def update_patient(patient_id):
    """Update patient information"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        old_values = patient.to_dict()
        
        # Update fields
        updateable = [
            'first_name', 'last_name', 'blood_group', 'phone', 'alternate_phone',
            'email', 'address', 'city', 'state', 'pincode',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'insurance_provider', 'insurance_id', 'allergies', 'chronic_conditions'
        ]
        
        for field in updateable:
            if field in data:
                setattr(patient, field, data[field])
        
        if 'gender' in data:
            patient.gender = Gender(data['gender'])
        
        if 'date_of_birth' in data:
            patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        log_action('patient_updated', 'patient', patient.id, old_values, patient.to_dict())
        
        return jsonify({
            'message': 'Patient updated successfully',
            'patient': patient.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'receptionist')
def delete_patient(patient_id):
    """Soft delete patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        patient.is_active = False
        db.session.commit()
        
        log_action('patient_deleted', 'patient', patient.id)
        
        return jsonify({'message': 'Patient deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== VITAL SIGNS ==============

@patients_bp.route('/<int:patient_id>/vitals', methods=['GET'])
@token_required
def get_patient_vitals(patient_id):
    """Get patient vital signs history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        vitals = VitalSigns.query.filter_by(patient_id=patient_id)\
            .order_by(VitalSigns.recorded_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'vitals': [v.to_dict() for v in vitals.items],
            'total': vitals.total,
            'pages': vitals.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>/vitals', methods=['POST'])
@token_required
def add_patient_vitals(patient_id):
    """Record patient vital signs"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        # Calculate BMI if weight and height provided
        bmi = None
        if data.get('weight') and data.get('height'):
            height_m = data['height'] / 100
            bmi = round(data['weight'] / (height_m ** 2), 2)
        
        vitals = VitalSigns(
            patient_id=patient_id,
            recorded_by=request.current_user.id,
            temperature=data.get('temperature'),
            blood_pressure_systolic=data.get('blood_pressure_systolic'),
            blood_pressure_diastolic=data.get('blood_pressure_diastolic'),
            pulse_rate=data.get('pulse_rate'),
            respiratory_rate=data.get('respiratory_rate'),
            oxygen_saturation=data.get('oxygen_saturation'),
            weight=data.get('weight'),
            height=data.get('height'),
            bmi=bmi,
            blood_sugar=data.get('blood_sugar'),
            notes=data.get('notes')
        )
        
        db.session.add(vitals)
        db.session.commit()
        
        log_action('vitals_recorded', 'vital_signs', vitals.id)
        
        return jsonify({
            'message': 'Vitals recorded successfully',
            'vitals': vitals.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== MEDICAL RECORDS (EMR) ==============

@patients_bp.route('/<int:patient_id>/medical-records', methods=['GET'])
@token_required
def get_medical_records(patient_id):
    """Get patient medical records history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        records = MedicalRecord.query.filter_by(patient_id=patient_id)\
            .order_by(MedicalRecord.visit_date.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'records': [r.to_dict() for r in records.items],
            'total': records.total,
            'pages': records.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>/medical-records', methods=['POST'])
@token_required
@role_required('doctor', 'admin')
def create_medical_record(patient_id):
    """Create a new medical record"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        record = MedicalRecord(
            patient_id=patient_id,
            doctor_id=request.current_user.id,
            appointment_id=data.get('appointment_id'),
            chief_complaint=data.get('chief_complaint'),
            history_of_present_illness=data.get('history_of_present_illness'),
            past_medical_history=data.get('past_medical_history'),
            family_history=data.get('family_history'),
            social_history=data.get('social_history'),
            physical_examination=data.get('physical_examination'),
            diagnosis=data.get('diagnosis'),
            icd_codes=data.get('icd_codes'),
            treatment_plan=data.get('treatment_plan'),
            follow_up_instructions=data.get('follow_up_instructions'),
            notes=data.get('notes'),
            ai_diagnosis_suggestion=data.get('ai_diagnosis_suggestion'),
            ai_risk_assessment=data.get('ai_risk_assessment')
        )
        
        if data.get('follow_up_date'):
            record.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
        
        db.session.add(record)
        db.session.commit()
        
        log_action('medical_record_created', 'medical_record', record.id)
        
        return jsonify({
            'message': 'Medical record created successfully',
            'record': record.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@patients_bp.route('/<int:patient_id>/medical-records/<int:record_id>', methods=['PUT'])
@token_required
@role_required('doctor', 'admin')
def update_medical_record(patient_id, record_id):
    """Update a medical record"""
    try:
        record = MedicalRecord.query.filter_by(
            id=record_id, 
            patient_id=patient_id
        ).first_or_404()
        
        data = request.get_json()
        
        updateable = [
            'chief_complaint', 'history_of_present_illness', 'past_medical_history',
            'family_history', 'social_history', 'physical_examination',
            'diagnosis', 'icd_codes', 'treatment_plan', 'follow_up_instructions',
            'notes', 'ai_diagnosis_suggestion', 'ai_risk_assessment'
        ]
        
        for field in updateable:
            if field in data:
                setattr(record, field, data[field])
        
        if 'follow_up_date' in data and data['follow_up_date']:
            record.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        
        log_action('medical_record_updated', 'medical_record', record.id)
        
        return jsonify({
            'message': 'Medical record updated successfully',
            'record': record.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== PATIENT SEARCH ==============

@patients_bp.route('/search', methods=['GET'])
@token_required
def search_patients():
    """Quick search patients by name, phone, or patient ID"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if len(query) < 2:
            return jsonify({'patients': []})
        
        search_filter = f"%{query}%"
        patients = Patient.query.filter(
            Patient.is_active == True,
            db.or_(
                Patient.first_name.ilike(search_filter),
                Patient.last_name.ilike(search_filter),
                Patient.patient_id.ilike(search_filter),
                Patient.phone.ilike(search_filter)
            )
        ).limit(limit).all()
        
        return jsonify({
            'patients': [p.to_dict() for p in patients]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== PATIENT STATISTICS ==============

@patients_bp.route('/stats', methods=['GET'])
@token_required
def patient_statistics():
    """Get patient statistics"""
    try:
        today = date.today()
        
        # Total patients
        total_patients = Patient.query.filter_by(is_active=True).count()
        
        # New patients today
        new_today = Patient.query.filter(
            Patient.is_active == True,
            db.func.date(Patient.created_at) == today
        ).count()
        
        # New this month
        start_of_month = today.replace(day=1)
        new_this_month = Patient.query.filter(
            Patient.is_active == True,
            Patient.created_at >= start_of_month
        ).count()
        
        # Gender distribution
        male_count = Patient.query.filter_by(gender=Gender.MALE, is_active=True).count()
        female_count = Patient.query.filter_by(gender=Gender.FEMALE, is_active=True).count()
        other_count = Patient.query.filter_by(gender=Gender.OTHER, is_active=True).count()
        
        return jsonify({
            'total_patients': total_patients,
            'new_today': new_today,
            'new_this_month': new_this_month,
            'gender_distribution': {
                'male': male_count,
                'female': female_count,
                'other': other_count
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
