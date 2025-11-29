"""
Reports & Dashboard Module for MedIntel Hospital Management System
Analytics, reports, AI-powered insights
"""

from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify
from models import (
    db, Patient, Appointment, Bill, Admission, LabOrder,
    Medicine, InventoryItem, User, Prescription,
    AppointmentStatus, AdmissionStatus, LabOrderStatus
)
from auth import token_required, role_required

reports_bp = Blueprint('reports', __name__)

# ============== DASHBOARD ==============

@reports_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard():
    """Get main dashboard statistics"""
    try:
        today = date.today()
        month_start = date(today.year, today.month, 1)
        
        # Patient stats
        total_patients = Patient.query.filter_by(is_active=True).count()
        new_patients_today = Patient.query.filter(
            db.func.date(Patient.created_at) == today
        ).count()
        new_patients_month = Patient.query.filter(
            Patient.created_at >= month_start
        ).count()
        
        # Appointment stats
        appointments_today = Appointment.query.filter(
            Appointment.appointment_date == today
        ).count()
        completed_today = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status == AppointmentStatus.COMPLETED
        ).count()
        pending_today = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CHECKED_IN])
        ).count()
        
        # IPD stats
        current_admissions = Admission.query.filter_by(
            status=AdmissionStatus.ADMITTED
        ).count()
        admissions_today = Admission.query.filter(
            db.func.date(Admission.admission_date) == today
        ).count()
        discharges_today = Admission.query.filter(
            Admission.status == AdmissionStatus.DISCHARGED,
            db.func.date(Admission.discharge_date) == today
        ).count()
        
        # Revenue stats
        today_revenue = db.session.query(
            db.func.sum(Bill.paid_amount)
        ).filter(
            db.func.date(Bill.created_at) == today
        ).scalar() or 0
        
        month_revenue = db.session.query(
            db.func.sum(Bill.paid_amount)
        ).filter(
            Bill.created_at >= month_start
        ).scalar() or 0
        
        pending_bills = Bill.query.filter(
            Bill.status.in_(['unpaid', 'partial'])
        ).count()
        
        # Lab stats
        pending_labs = LabOrder.query.filter_by(
            status=LabOrderStatus.PENDING
        ).count()
        labs_today = LabOrder.query.filter(
            db.func.date(LabOrder.created_at) == today
        ).count()
        
        # Pharmacy stats
        low_stock_medicines = Medicine.query.filter(
            Medicine.is_active == True,
            Medicine.stock_quantity <= Medicine.reorder_level
        ).count()
        
        # Staff stats
        total_doctors = User.query.filter_by(role='doctor', is_active=True).count()
        total_nurses = User.query.filter_by(role='nurse', is_active=True).count()
        total_staff = User.query.filter_by(is_active=True).count()
        
        return jsonify({
            'patients': {
                'total': total_patients,
                'new_today': new_patients_today,
                'new_this_month': new_patients_month
            },
            'appointments': {
                'today': appointments_today,
                'completed': completed_today,
                'pending': pending_today
            },
            'ipd': {
                'current_admissions': current_admissions,
                'admissions_today': admissions_today,
                'discharges_today': discharges_today
            },
            'revenue': {
                'today': float(today_revenue),
                'this_month': float(month_revenue),
                'pending_bills': pending_bills
            },
            'lab': {
                'pending_tests': pending_labs,
                'tests_today': labs_today
            },
            'pharmacy': {
                'low_stock_alerts': low_stock_medicines
            },
            'staff': {
                'doctors': total_doctors,
                'nurses': total_nurses,
                'total': total_staff
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== PATIENT REPORTS ==============

@reports_bp.route('/patients/summary', methods=['GET'])
@token_required
def patient_summary():
    """Get patient summary report"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        # Registration trend
        daily_registrations = db.session.query(
            db.func.date(Patient.created_at).label('date'),
            db.func.count(Patient.id).label('count')
        ).filter(
            Patient.created_at >= start_date
        ).group_by(
            db.func.date(Patient.created_at)
        ).all()
        
        # Gender distribution
        gender_dist = db.session.query(
            Patient.gender,
            db.func.count(Patient.id)
        ).filter(Patient.is_active == True).group_by(Patient.gender).all()
        
        # Blood group distribution
        blood_dist = db.session.query(
            Patient.blood_group,
            db.func.count(Patient.id)
        ).filter(
            Patient.is_active == True,
            Patient.blood_group != None
        ).group_by(Patient.blood_group).all()
        
        return jsonify({
            'registration_trend': [
                {'date': str(r[0]), 'count': r[1]} for r in daily_registrations
            ],
            'gender_distribution': [
                {'gender': g[0] or 'Unknown', 'count': g[1]} for g in gender_dist
            ],
            'blood_group_distribution': [
                {'blood_group': b[0], 'count': b[1]} for b in blood_dist
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== APPOINTMENT REPORTS ==============

@reports_bp.route('/appointments/summary', methods=['GET'])
@token_required
def appointment_summary():
    """Get appointment summary report"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        # Daily appointments
        daily_appointments = db.session.query(
            Appointment.appointment_date,
            db.func.count(Appointment.id)
        ).filter(
            Appointment.appointment_date >= start_date
        ).group_by(Appointment.appointment_date).all()
        
        # Status distribution
        status_dist = db.session.query(
            Appointment.status,
            db.func.count(Appointment.id)
        ).filter(
            Appointment.appointment_date >= start_date
        ).group_by(Appointment.status).all()
        
        # Doctor-wise appointments
        doctor_appointments = db.session.query(
            User.full_name,
            db.func.count(Appointment.id)
        ).join(User, Appointment.doctor_id == User.id).filter(
            Appointment.appointment_date >= start_date
        ).group_by(User.full_name).all()
        
        return jsonify({
            'daily_trend': [
                {'date': str(a[0]), 'count': a[1]} for a in daily_appointments
            ],
            'status_distribution': [
                {'status': s[0].value if s[0] else 'Unknown', 'count': s[1]} for s in status_dist
            ],
            'doctor_wise': [
                {'doctor': d[0], 'appointments': d[1]} for d in doctor_appointments
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== REVENUE REPORTS ==============

@reports_bp.route('/revenue/summary', methods=['GET'])
@token_required
@role_required('admin', 'accountant')
def revenue_summary():
    """Get revenue summary report"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        # Daily revenue
        daily_revenue = db.session.query(
            db.func.date(Bill.created_at).label('date'),
            db.func.sum(Bill.total_amount).label('total'),
            db.func.sum(Bill.paid_amount).label('collected')
        ).filter(
            Bill.created_at >= start_date
        ).group_by(db.func.date(Bill.created_at)).all()
        
        # Department-wise revenue
        department_revenue = db.session.query(
            Bill.bill_type,
            db.func.sum(Bill.total_amount)
        ).filter(
            Bill.created_at >= start_date
        ).group_by(Bill.bill_type).all()
        
        # Payment method distribution
        payment_dist = db.session.query(
            Bill.payment_method,
            db.func.sum(Bill.paid_amount)
        ).filter(
            Bill.created_at >= start_date,
            Bill.payment_method != None
        ).group_by(Bill.payment_method).all()
        
        # Outstanding amounts
        outstanding = db.session.query(
            db.func.sum(Bill.total_amount - Bill.paid_amount)
        ).filter(
            Bill.status.in_(['unpaid', 'partial'])
        ).scalar() or 0
        
        return jsonify({
            'daily_revenue': [
                {
                    'date': str(r[0]),
                    'total': float(r[1] or 0),
                    'collected': float(r[2] or 0)
                } for r in daily_revenue
            ],
            'department_wise': [
                {'department': d[0] or 'Other', 'amount': float(d[1] or 0)} for d in department_revenue
            ],
            'payment_methods': [
                {'method': p[0], 'amount': float(p[1] or 0)} for p in payment_dist
            ],
            'outstanding_amount': float(outstanding)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== IPD REPORTS ==============

@reports_bp.route('/ipd/summary', methods=['GET'])
@token_required
def ipd_summary():
    """Get IPD summary report"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        # Daily admissions
        daily_admissions = db.session.query(
            db.func.date(Admission.admission_date),
            db.func.count(Admission.id)
        ).filter(
            Admission.admission_date >= start_date
        ).group_by(db.func.date(Admission.admission_date)).all()
        
        # Average length of stay
        completed_admissions = Admission.query.filter(
            Admission.status == AdmissionStatus.DISCHARGED,
            Admission.discharge_date != None,
            Admission.admission_date >= start_date
        ).all()
        
        if completed_admissions:
            total_days = sum([
                (a.discharge_date - a.admission_date).days 
                for a in completed_admissions if a.discharge_date and a.admission_date
            ])
            avg_los = total_days / len(completed_admissions)
        else:
            avg_los = 0
        
        return jsonify({
            'daily_admissions': [
                {'date': str(a[0]), 'count': a[1]} for a in daily_admissions
            ],
            'average_length_of_stay': round(avg_los, 1)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== LAB REPORTS ==============

@reports_bp.route('/lab/summary', methods=['GET'])
@token_required
def lab_summary():
    """Get lab summary report"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)
        
        # Daily tests
        daily_tests = db.session.query(
            db.func.date(LabOrder.created_at),
            db.func.count(LabOrder.id)
        ).filter(
            LabOrder.created_at >= start_date
        ).group_by(db.func.date(LabOrder.created_at)).all()
        
        # Status distribution
        status_dist = db.session.query(
            LabOrder.status,
            db.func.count(LabOrder.id)
        ).filter(
            LabOrder.created_at >= start_date
        ).group_by(LabOrder.status).all()
        
        return jsonify({
            'daily_tests': [
                {'date': str(t[0]), 'count': t[1]} for t in daily_tests
            ],
            'status_distribution': [
                {'status': s[0].value if s[0] else 'Unknown', 'count': s[1]} for s in status_dist
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== AI INSIGHTS ==============

@reports_bp.route('/ai-insights', methods=['GET'])
@token_required
def get_ai_insights():
    """Get AI-powered insights from integrated agents"""
    try:
        insights = []
        
        # Triage insights
        try:
            from routes.ai_integration import get_triage_summary
            triage_data = get_triage_summary()
            if triage_data:
                insights.append({
                    'agent': 'Triage Agent',
                    'type': 'patient_priority',
                    'data': triage_data
                })
        except:
            pass
        
        # Outbreak prediction
        try:
            from routes.ai_integration import get_outbreak_prediction
            outbreak_data = get_outbreak_prediction()
            if outbreak_data:
                insights.append({
                    'agent': 'Predictive Outbreak Agent',
                    'type': 'disease_prediction',
                    'data': outbreak_data
                })
        except:
            pass
        
        # Inventory forecast
        try:
            from routes.ai_integration import get_inventory_forecast
            inventory_data = get_inventory_forecast()
            if inventory_data:
                insights.append({
                    'agent': 'Forecasting Agent',
                    'type': 'inventory_forecast',
                    'data': inventory_data
                })
        except:
            pass
        
        # Staff optimization
        try:
            from routes.ai_integration import get_staff_recommendations
            staff_data = get_staff_recommendations()
            if staff_data:
                insights.append({
                    'agent': 'Staff Optimization Agent',
                    'type': 'staff_scheduling',
                    'data': staff_data
                })
        except:
            pass
        
        return jsonify({'insights': insights})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== EXPORT REPORTS ==============

@reports_bp.route('/export/<report_type>', methods=['GET'])
@token_required
@role_required('admin', 'accountant')
def export_report(report_type):
    """Export report data (JSON format for now)"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = date.today() - timedelta(days=30)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date = date.today()
        
        data = {}
        
        if report_type == 'patients':
            patients = Patient.query.filter(
                Patient.created_at >= start_date,
                Patient.created_at <= end_date
            ).all()
            data = {'patients': [p.to_dict() for p in patients]}
        
        elif report_type == 'appointments':
            appointments = Appointment.query.filter(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date
            ).all()
            data = {'appointments': [a.to_dict() for a in appointments]}
        
        elif report_type == 'bills':
            bills = Bill.query.filter(
                Bill.created_at >= start_date,
                Bill.created_at <= end_date
            ).all()
            data = {'bills': [b.to_dict() for b in bills]}
        
        elif report_type == 'lab':
            lab_orders = LabOrder.query.filter(
                LabOrder.created_at >= start_date,
                LabOrder.created_at <= end_date
            ).all()
            data = {'lab_orders': [l.to_dict() for l in lab_orders]}
        
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        data['report_meta'] = {
            'type': report_type,
            'start_date': str(start_date),
            'end_date': str(end_date),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
