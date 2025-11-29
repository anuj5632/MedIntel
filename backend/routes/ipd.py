"""
In-Patient Department (IPD) Module for MedIntel Hospital Management System
Admissions, bed management, discharge
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify
from models import (
    db, Admission, Ward, Bed, Patient, User,
    AdmissionStatus, generate_id
)
from auth import token_required, role_required, log_action

ipd_bp = Blueprint('ipd', __name__)

# ============== WARDS ==============

@ipd_bp.route('/wards', methods=['GET'])
@token_required
def list_wards():
    """List all wards"""
    try:
        wards = Ward.query.filter_by(is_active=True).all()
        
        ward_list = []
        for ward in wards:
            ward_data = ward.to_dict()
            ward_data['available_beds'] = Bed.query.filter_by(
                ward_id=ward.id,
                is_occupied=False,
                is_active=True
            ).count()
            ward_list.append(ward_data)
        
        return jsonify({'wards': ward_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ipd_bp.route('/wards', methods=['POST'])
@token_required
@role_required('admin')
def create_ward():
    """Create a new ward"""
    try:
        data = request.get_json()
        
        ward = Ward(
            name=data['name'],
            ward_type=data.get('ward_type'),
            floor=data.get('floor'),
            total_beds=data.get('total_beds', 0),
            charge_per_day=data.get('charge_per_day'),
            description=data.get('description')
        )
        
        db.session.add(ward)
        db.session.commit()
        
        log_action('ward_created', 'ward', ward.id)
        
        return jsonify({
            'message': 'Ward created successfully',
            'ward': ward.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== BEDS ==============

@ipd_bp.route('/beds', methods=['GET'])
@token_required
def list_beds():
    """List all beds with occupancy status"""
    try:
        ward_id = request.args.get('ward_id', type=int)
        available_only = request.args.get('available', type=bool)
        
        query = Bed.query.filter_by(is_active=True)
        
        if ward_id:
            query = query.filter(Bed.ward_id == ward_id)
        
        if available_only:
            query = query.filter(Bed.is_occupied == False)
        
        beds = query.all()
        
        return jsonify({'beds': [b.to_dict() for b in beds]})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ipd_bp.route('/beds', methods=['POST'])
@token_required
@role_required('admin')
def create_bed():
    """Create a new bed"""
    try:
        data = request.get_json()
        
        bed = Bed(
            bed_number=data['bed_number'],
            ward_id=data['ward_id'],
            bed_type=data.get('bed_type', 'Regular')
        )
        
        db.session.add(bed)
        
        # Update ward total beds
        ward = Ward.query.get(data['ward_id'])
        if ward:
            ward.total_beds = Bed.query.filter_by(ward_id=ward.id, is_active=True).count() + 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Bed created successfully',
            'bed': bed.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== ADMISSIONS ==============

@ipd_bp.route('/admissions', methods=['GET'])
@token_required
def list_admissions():
    """List admissions"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        ward_id = request.args.get('ward_id', type=int)
        
        query = Admission.query
        
        if status:
            query = query.filter(Admission.status == AdmissionStatus(status))
        
        if ward_id:
            query = query.join(Bed).filter(Bed.ward_id == ward_id)
        
        admissions = query.order_by(Admission.admission_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'admissions': [a.to_dict() for a in admissions.items],
            'total': admissions.total,
            'pages': admissions.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ipd_bp.route('/admissions', methods=['POST'])
@token_required
@role_required('doctor', 'admin', 'receptionist')
def create_admission():
    """Admit a patient"""
    try:
        data = request.get_json()
        
        # Validate patient
        patient = Patient.query.get(data.get('patient_id'))
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Validate bed
        bed = Bed.query.get(data.get('bed_id'))
        if not bed:
            return jsonify({'error': 'Bed not found'}), 404
        
        if bed.is_occupied:
            return jsonify({'error': 'Bed is already occupied'}), 400
        
        # Validate doctor
        doctor = User.query.get(data.get('admitting_doctor_id'))
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        
        admission_id = generate_id('ADM', Admission)
        
        admission = Admission(
            admission_id=admission_id,
            patient_id=data['patient_id'],
            bed_id=data['bed_id'],
            admitting_doctor_id=data['admitting_doctor_id'],
            admission_reason=data.get('admission_reason'),
            admission_diagnosis=data.get('admission_diagnosis'),
            status=AdmissionStatus.ADMITTED
        )
        
        if data.get('expected_discharge_date'):
            admission.expected_discharge_date = datetime.strptime(
                data['expected_discharge_date'], '%Y-%m-%d'
            ).date()
        
        # Mark bed as occupied
        bed.is_occupied = True
        
        db.session.add(admission)
        db.session.commit()
        
        log_action('patient_admitted', 'admission', admission.id)
        
        return jsonify({
            'message': 'Patient admitted successfully',
            'admission': admission.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ipd_bp.route('/admissions/<int:admission_id>', methods=['GET'])
@token_required
def get_admission(admission_id):
    """Get admission details"""
    try:
        admission = Admission.query.get_or_404(admission_id)
        return jsonify({'admission': admission.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ipd_bp.route('/admissions/<int:admission_id>/discharge', methods=['POST'])
@token_required
@role_required('doctor', 'admin')
def discharge_patient(admission_id):
    """Discharge a patient"""
    try:
        admission = Admission.query.get_or_404(admission_id)
        data = request.get_json() or {}
        
        if admission.status != AdmissionStatus.ADMITTED:
            return jsonify({'error': 'Patient is not currently admitted'}), 400
        
        admission.status = AdmissionStatus.DISCHARGED
        admission.discharge_date = datetime.utcnow()
        admission.discharge_diagnosis = data.get('discharge_diagnosis')
        admission.discharge_summary = data.get('discharge_summary')
        
        # Free the bed
        if admission.bed:
            admission.bed.is_occupied = False
        
        db.session.commit()
        
        log_action('patient_discharged', 'admission', admission.id)
        
        return jsonify({
            'message': 'Patient discharged successfully',
            'admission': admission.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ipd_bp.route('/admissions/<int:admission_id>/transfer', methods=['POST'])
@token_required
@role_required('doctor', 'admin', 'nurse')
def transfer_patient(admission_id):
    """Transfer patient to another bed"""
    try:
        admission = Admission.query.get_or_404(admission_id)
        data = request.get_json()
        
        new_bed_id = data.get('new_bed_id')
        if not new_bed_id:
            return jsonify({'error': 'New bed ID required'}), 400
        
        new_bed = Bed.query.get(new_bed_id)
        if not new_bed:
            return jsonify({'error': 'New bed not found'}), 404
        
        if new_bed.is_occupied:
            return jsonify({'error': 'New bed is occupied'}), 400
        
        # Free old bed
        if admission.bed:
            admission.bed.is_occupied = False
        
        # Assign new bed
        admission.bed_id = new_bed_id
        new_bed.is_occupied = True
        
        db.session.commit()
        
        log_action('patient_transferred', 'admission', admission.id)
        
        return jsonify({
            'message': 'Patient transferred successfully',
            'admission': admission.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== IPD STATISTICS ==============

@ipd_bp.route('/stats', methods=['GET'])
@token_required
def ipd_statistics():
    """Get IPD statistics"""
    try:
        # Current admissions
        current_admissions = Admission.query.filter_by(
            status=AdmissionStatus.ADMITTED
        ).count()
        
        # Total beds
        total_beds = Bed.query.filter_by(is_active=True).count()
        
        # Occupied beds
        occupied_beds = Bed.query.filter_by(is_active=True, is_occupied=True).count()
        
        # Available beds
        available_beds = total_beds - occupied_beds
        
        # Today's admissions
        today = date.today()
        today_admissions = Admission.query.filter(
            db.func.date(Admission.admission_date) == today
        ).count()
        
        # Today's discharges
        today_discharges = Admission.query.filter(
            Admission.status == AdmissionStatus.DISCHARGED,
            db.func.date(Admission.discharge_date) == today
        ).count()
        
        # Ward-wise occupancy
        wards = Ward.query.filter_by(is_active=True).all()
        ward_occupancy = []
        for ward in wards:
            ward_total = Bed.query.filter_by(ward_id=ward.id, is_active=True).count()
            ward_occupied = Bed.query.filter_by(ward_id=ward.id, is_active=True, is_occupied=True).count()
            ward_occupancy.append({
                'ward_name': ward.name,
                'total_beds': ward_total,
                'occupied': ward_occupied,
                'available': ward_total - ward_occupied,
                'occupancy_rate': round((ward_occupied / ward_total * 100) if ward_total > 0 else 0, 1)
            })
        
        return jsonify({
            'current_admissions': current_admissions,
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'available_beds': available_beds,
            'occupancy_rate': round((occupied_beds / total_beds * 100) if total_beds > 0 else 0, 1),
            'today_admissions': today_admissions,
            'today_discharges': today_discharges,
            'ward_occupancy': ward_occupancy
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ipd_bp.route('/current-patients', methods=['GET'])
@token_required
def get_current_patients():
    """Get list of currently admitted patients"""
    try:
        admissions = Admission.query.filter_by(
            status=AdmissionStatus.ADMITTED
        ).order_by(Admission.admission_date.desc()).all()
        
        return jsonify({
            'patients': [a.to_dict() for a in admissions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
