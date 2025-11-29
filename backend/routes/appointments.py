"""
Appointment Management Module for MedIntel Hospital Management System
Scheduling, queue management, and appointment tracking
"""

from datetime import datetime, date, time, timedelta
from flask import Blueprint, request, jsonify
from models import (
    db, Appointment, Patient, User, UserRole,
    AppointmentStatus, generate_id
)
from auth import token_required, role_required, log_action

appointments_bp = Blueprint('appointments', __name__)

# ============== APPOINTMENT CRUD ==============

@appointments_bp.route('', methods=['GET'])
@token_required
def list_appointments():
    """List appointments with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filters
        date_filter = request.args.get('date')
        doctor_id = request.args.get('doctor_id', type=int)
        patient_id = request.args.get('patient_id', type=int)
        status = request.args.get('status')
        department = request.args.get('department')
        
        query = Appointment.query
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(Appointment.appointment_date == filter_date)
            except:
                pass
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        
        if status:
            query = query.filter(Appointment.status == AppointmentStatus(status))
        
        if department:
            query = query.filter(Appointment.department == department)
        
        # If user is a doctor, only show their appointments
        if request.current_user.role == UserRole.DOCTOR:
            query = query.filter(Appointment.doctor_id == request.current_user.id)
        
        appointments = query.order_by(
            Appointment.appointment_date.desc(),
            Appointment.appointment_time.asc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'appointments': [a.to_dict() for a in appointments.items],
            'total': appointments.total,
            'pages': appointments.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('', methods=['POST'])
@token_required
def create_appointment():
    """Schedule a new appointment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['patient_id', 'doctor_id', 'appointment_date', 'appointment_time']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate patient exists
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Validate doctor exists and is a doctor
        doctor = User.query.get(data['doctor_id'])
        if not doctor or doctor.role != UserRole.DOCTOR:
            return jsonify({'error': 'Doctor not found'}), 404
        
        # Parse date and time
        try:
            apt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
            apt_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        except:
            return jsonify({'error': 'Invalid date/time format'}), 400
        
        # Check for scheduling conflicts
        conflict = Appointment.query.filter(
            Appointment.doctor_id == data['doctor_id'],
            Appointment.appointment_date == apt_date,
            Appointment.appointment_time == apt_time,
            Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW])
        ).first()
        
        if conflict:
            return jsonify({'error': 'Time slot already booked'}), 400
        
        # Generate appointment ID and token number
        appointment_id = generate_id('APT', Appointment)
        
        # Get token number for the day
        token_count = Appointment.query.filter(
            Appointment.doctor_id == data['doctor_id'],
            Appointment.appointment_date == apt_date
        ).count()
        token_number = token_count + 1
        
        appointment = Appointment(
            appointment_id=appointment_id,
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            department=data.get('department') or doctor.department,
            appointment_date=apt_date,
            appointment_time=apt_time,
            duration_minutes=data.get('duration_minutes', 15),
            appointment_type=data.get('appointment_type', 'consultation'),
            chief_complaint=data.get('chief_complaint'),
            notes=data.get('notes'),
            token_number=token_number,
            is_telemedicine=data.get('is_telemedicine', False),
            status=AppointmentStatus.SCHEDULED
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        log_action('appointment_created', 'appointment', appointment.id)
        
        return jsonify({
            'message': 'Appointment scheduled successfully',
            'appointment': appointment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['GET'])
@token_required
def get_appointment(appointment_id):
    """Get appointment details"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        return jsonify({'appointment': appointment.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>', methods=['PUT'])
@token_required
def update_appointment(appointment_id):
    """Update appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json()
        
        # Update status
        if 'status' in data:
            appointment.status = AppointmentStatus(data['status'])
            
            # Set check-in/check-out times based on status
            if data['status'] == 'in_progress':
                appointment.check_in_time = datetime.utcnow()
            elif data['status'] == 'completed':
                appointment.check_out_time = datetime.utcnow()
        
        # Update other fields
        if 'appointment_date' in data:
            appointment.appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        
        if 'appointment_time' in data:
            appointment.appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        if 'chief_complaint' in data:
            appointment.chief_complaint = data['chief_complaint']
        
        if 'notes' in data:
            appointment.notes = data['notes']
        
        if 'triage_priority' in data:
            appointment.triage_priority = data['triage_priority']
        
        if 'triage_recommendation' in data:
            appointment.triage_recommendation = data['triage_recommendation']
        
        db.session.commit()
        
        log_action('appointment_updated', 'appointment', appointment.id)
        
        return jsonify({
            'message': 'Appointment updated successfully',
            'appointment': appointment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@appointments_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@token_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json() or {}
        
        if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            return jsonify({'error': 'Cannot cancel this appointment'}), 400
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.notes = (appointment.notes or '') + f"\nCancellation reason: {data.get('reason', 'Not specified')}"
        
        db.session.commit()
        
        log_action('appointment_cancelled', 'appointment', appointment.id)
        
        return jsonify({'message': 'Appointment cancelled successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== TODAY'S QUEUE ==============

@appointments_bp.route('/today', methods=['GET'])
@token_required
def get_todays_appointments():
    """Get today's appointments for queue management"""
    try:
        today = date.today()
        doctor_id = request.args.get('doctor_id', type=int)
        
        query = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status.notin_([AppointmentStatus.CANCELLED])
        )
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        elif request.current_user.role == UserRole.DOCTOR:
            query = query.filter(Appointment.doctor_id == request.current_user.id)
        
        appointments = query.order_by(
            Appointment.appointment_time.asc()
        ).all()
        
        # Categorize by status
        waiting = [a.to_dict() for a in appointments if a.status == AppointmentStatus.SCHEDULED]
        in_progress = [a.to_dict() for a in appointments if a.status == AppointmentStatus.IN_PROGRESS]
        completed = [a.to_dict() for a in appointments if a.status == AppointmentStatus.COMPLETED]
        
        return jsonify({
            'date': today.isoformat(),
            'waiting': waiting,
            'in_progress': in_progress,
            'completed': completed,
            'total_scheduled': len(waiting) + len(in_progress),
            'total_completed': len(completed)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== AVAILABLE SLOTS ==============

@appointments_bp.route('/available-slots', methods=['GET'])
@token_required
def get_available_slots():
    """Get available appointment slots for a doctor on a date"""
    try:
        doctor_id = request.args.get('doctor_id', type=int)
        date_str = request.args.get('date')
        
        if not doctor_id or not date_str:
            return jsonify({'error': 'doctor_id and date are required'}), 400
        
        try:
            slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Define working hours (9 AM to 5 PM, 15-minute slots)
        start_hour = 9
        end_hour = 17
        slot_duration = 15
        
        # Generate all possible slots
        all_slots = []
        current_time = datetime.combine(slot_date, time(start_hour, 0))
        end_time = datetime.combine(slot_date, time(end_hour, 0))
        
        while current_time < end_time:
            all_slots.append(current_time.time())
            current_time += timedelta(minutes=slot_duration)
        
        # Get booked slots
        booked = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == slot_date,
            Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW])
        ).all()
        
        booked_times = [a.appointment_time for a in booked]
        
        # Filter available slots
        available = [
            t.strftime('%H:%M') for t in all_slots 
            if t not in booked_times and (slot_date > date.today() or t > datetime.now().time())
        ]
        
        return jsonify({
            'date': slot_date.isoformat(),
            'doctor_id': doctor_id,
            'available_slots': available,
            'total_slots': len(all_slots),
            'booked_slots': len(booked_times)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== APPOINTMENT STATISTICS ==============

@appointments_bp.route('/stats', methods=['GET'])
@token_required
def appointment_statistics():
    """Get appointment statistics"""
    try:
        today = date.today()
        
        # Today's stats
        today_total = Appointment.query.filter(
            Appointment.appointment_date == today
        ).count()
        
        today_completed = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status == AppointmentStatus.COMPLETED
        ).count()
        
        today_cancelled = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status == AppointmentStatus.CANCELLED
        ).count()
        
        # This week
        start_of_week = today - timedelta(days=today.weekday())
        week_total = Appointment.query.filter(
            Appointment.appointment_date >= start_of_week,
            Appointment.appointment_date <= today
        ).count()
        
        # Department-wise today
        dept_stats = db.session.query(
            Appointment.department,
            db.func.count(Appointment.id)
        ).filter(
            Appointment.appointment_date == today
        ).group_by(Appointment.department).all()
        
        return jsonify({
            'today': {
                'total': today_total,
                'completed': today_completed,
                'cancelled': today_cancelled,
                'pending': today_total - today_completed - today_cancelled
            },
            'this_week': week_total,
            'department_wise': {dept: count for dept, count in dept_stats if dept}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== RESCHEDULE ==============

@appointments_bp.route('/<int:appointment_id>/reschedule', methods=['POST'])
@token_required
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json()
        
        if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            return jsonify({'error': 'Cannot reschedule this appointment'}), 400
        
        # Validate new date and time
        new_date = datetime.strptime(data['new_date'], '%Y-%m-%d').date()
        new_time = datetime.strptime(data['new_time'], '%H:%M').time()
        
        # Check for conflicts
        conflict = Appointment.query.filter(
            Appointment.id != appointment_id,
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == new_date,
            Appointment.appointment_time == new_time,
            Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW])
        ).first()
        
        if conflict:
            return jsonify({'error': 'New time slot is not available'}), 400
        
        # Update appointment
        old_date = appointment.appointment_date
        old_time = appointment.appointment_time
        
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.notes = (appointment.notes or '') + f"\nRescheduled from {old_date} {old_time} to {new_date} {new_time}"
        
        db.session.commit()
        
        log_action('appointment_rescheduled', 'appointment', appointment.id)
        
        return jsonify({
            'message': 'Appointment rescheduled successfully',
            'appointment': appointment.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
