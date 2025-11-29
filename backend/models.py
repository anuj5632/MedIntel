"""
Database Models for MedIntel Hospital Management System
Complete hospital management with authentication and all modules
"""

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

# ============== ENUMS ==============

class UserRole(enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    PHARMACIST = "pharmacist"
    LAB_TECH = "lab_tech"
    ACCOUNTANT = "accountant"

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"

class AdmissionStatus(enum.Enum):
    ADMITTED = "admitted"
    DISCHARGED = "discharged"
    TRANSFERRED = "transferred"

class LabTestStatus(enum.Enum):
    ORDERED = "ordered"
    SAMPLE_COLLECTED = "sample_collected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELIVERED = "delivered"

# Alias for compatibility with routes
LabOrderStatus = LabTestStatus

# ============== USER & AUTHENTICATION ==============

class User(UserMixin, db.Model):
    """User model for authentication and role management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.RECEPTIONIST)
    department = db.Column(db.String(100))
    specialization = db.Column(db.String(100))  # For doctors
    license_number = db.Column(db.String(50))  # For doctors/nurses
    is_active = db.Column(db.Boolean, default=True)
    profile_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    appointments_as_doctor = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', backref='doctor', lazy='dynamic')
    prescriptions = db.relationship('Prescription', foreign_keys='Prescription.doctor_id', backref='doctor', lazy='dynamic')
    dispensed_prescriptions = db.relationship('Prescription', foreign_keys='Prescription.dispensed_by', backref='dispenser', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role.value if self.role else None,
            'department': self.department,
            'specialization': self.specialization,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============== PATIENT MANAGEMENT ==============

class Patient(db.Model):
    """Patient registration and demographics"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False, index=True)  # MRN/UHID
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    blood_group = db.Column(db.String(5))
    phone = db.Column(db.String(20), nullable=False)
    alternate_phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relation = db.Column(db.String(50))
    insurance_provider = db.Column(db.String(100))
    insurance_id = db.Column(db.String(50))
    allergies = db.Column(db.Text)
    chronic_conditions = db.Column(db.Text)
    profile_image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic')
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic')
    prescriptions = db.relationship('Prescription', backref='patient', lazy='dynamic')
    lab_orders = db.relationship('LabOrder', backref='patient', lazy='dynamic')
    bills = db.relationship('Bill', backref='patient', lazy='dynamic')
    admissions = db.relationship('Admission', backref='patient', lazy='dynamic')
    vitals = db.relationship('VitalSigns', backref='patient', lazy='dynamic')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,
            'gender': self.gender.value if self.gender else None,
            'blood_group': self.blood_group,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'allergies': self.allergies,
            'chronic_conditions': self.chronic_conditions,
            'insurance_provider': self.insurance_provider,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============== VITAL SIGNS ==============

class VitalSigns(db.Model):
    """Patient vital signs records"""
    __tablename__ = 'vital_signs'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    temperature = db.Column(db.Float)  # Celsius
    blood_pressure_systolic = db.Column(db.Integer)
    blood_pressure_diastolic = db.Column(db.Integer)
    pulse_rate = db.Column(db.Integer)
    respiratory_rate = db.Column(db.Integer)
    oxygen_saturation = db.Column(db.Float)
    weight = db.Column(db.Float)  # kg
    height = db.Column(db.Float)  # cm
    bmi = db.Column(db.Float)
    blood_sugar = db.Column(db.Float)
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'temperature': self.temperature,
            'blood_pressure': f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}" if self.blood_pressure_systolic else None,
            'pulse_rate': self.pulse_rate,
            'respiratory_rate': self.respiratory_rate,
            'oxygen_saturation': self.oxygen_saturation,
            'weight': self.weight,
            'height': self.height,
            'bmi': self.bmi,
            'blood_sugar': self.blood_sugar,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }

# ============== APPOINTMENTS ==============

class Appointment(db.Model):
    """Appointment scheduling and management"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(100))
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=15)
    appointment_type = db.Column(db.String(50))  # consultation, follow-up, emergency
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    chief_complaint = db.Column(db.Text)
    notes = db.Column(db.Text)
    token_number = db.Column(db.Integer)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    is_telemedicine = db.Column(db.Boolean, default=False)
    telemedicine_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # AI Agent Integration
    triage_priority = db.Column(db.String(20))  # From Triage Agent
    triage_recommendation = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if self.doctor else None,
            'department': self.department,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'duration_minutes': self.duration_minutes,
            'appointment_type': self.appointment_type,
            'status': self.status.value if self.status else None,
            'chief_complaint': self.chief_complaint,
            'token_number': self.token_number,
            'is_telemedicine': self.is_telemedicine,
            'triage_priority': self.triage_priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============== MEDICAL RECORDS (EMR) ==============

class MedicalRecord(db.Model):
    """Electronic Medical Records"""
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    chief_complaint = db.Column(db.Text)
    history_of_present_illness = db.Column(db.Text)
    past_medical_history = db.Column(db.Text)
    family_history = db.Column(db.Text)
    social_history = db.Column(db.Text)
    physical_examination = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    icd_codes = db.Column(db.String(255))  # ICD-10 codes
    treatment_plan = db.Column(db.Text)
    follow_up_instructions = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    # AI Agent Integration
    ai_diagnosis_suggestion = db.Column(db.Text)  # From diagnostic agents
    ai_risk_assessment = db.Column(db.Text)  # From prediction agents
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'chief_complaint': self.chief_complaint,
            'diagnosis': self.diagnosis,
            'icd_codes': self.icd_codes,
            'treatment_plan': self.treatment_plan,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'ai_diagnosis_suggestion': self.ai_diagnosis_suggestion,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============== PRESCRIPTIONS ==============

class Prescription(db.Model):
    """Prescription management"""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'))
    prescription_date = db.Column(db.DateTime, default=datetime.utcnow)
    diagnosis = db.Column(db.Text)
    notes = db.Column(db.Text)
    is_dispensed = db.Column(db.Boolean, default=False)
    dispensed_at = db.Column(db.DateTime)
    dispensed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('PrescriptionItem', backref='prescription', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'prescription_id': self.prescription_id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'doctor_id': self.doctor_id,
            'doctor_name': self.doctor.full_name if self.doctor else None,
            'prescription_date': self.prescription_date.isoformat() if self.prescription_date else None,
            'diagnosis': self.diagnosis,
            'is_dispensed': self.is_dispensed,
            'items': [item.to_dict() for item in self.items]
        }

class PrescriptionItem(db.Model):
    """Individual prescription items/medications"""
    __tablename__ = 'prescription_items'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'))
    medicine_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))  # e.g., "1-0-1", "TID", "BID"
    duration = db.Column(db.String(50))  # e.g., "7 days", "2 weeks"
    quantity = db.Column(db.Integer)
    instructions = db.Column(db.Text)  # e.g., "Take after meals"
    is_dispensed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'medicine_name': self.medicine_name,
            'dosage': self.dosage,
            'frequency': self.frequency,
            'duration': self.duration,
            'quantity': self.quantity,
            'instructions': self.instructions,
            'is_dispensed': self.is_dispensed
        }

# ============== PHARMACY/MEDICINES ==============

class Medicine(db.Model):
    """Medicine/Drug inventory"""
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    generic_name = db.Column(db.String(200))
    brand = db.Column(db.String(100))
    category = db.Column(db.String(100))  # Tablet, Syrup, Injection, etc.
    composition = db.Column(db.Text)
    strength = db.Column(db.String(50))  # e.g., "500mg", "10ml"
    unit = db.Column(db.String(20))  # Tablet, Bottle, Vial
    manufacturer = db.Column(db.String(200))
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    mrp = db.Column(db.Float)
    purchase_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    quantity_in_stock = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    storage_location = db.Column(db.String(100))
    requires_prescription = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'generic_name': self.generic_name,
            'brand': self.brand,
            'category': self.category,
            'strength': self.strength,
            'manufacturer': self.manufacturer,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'mrp': self.mrp,
            'selling_price': self.selling_price,
            'quantity_in_stock': self.quantity_in_stock,
            'reorder_level': self.reorder_level,
            'is_low_stock': self.quantity_in_stock <= self.reorder_level
        }

# ============== LAB/DIAGNOSTICS ==============

class LabTest(db.Model):
    """Lab test catalog"""
    __tablename__ = 'lab_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    test_code = db.Column(db.String(20), unique=True, nullable=False)
    test_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # Hematology, Biochemistry, Microbiology, etc.
    sample_type = db.Column(db.String(100))  # Blood, Urine, Stool, etc.
    sample_volume = db.Column(db.String(50))
    container_type = db.Column(db.String(100))
    turnaround_time = db.Column(db.String(50))  # e.g., "2 hours", "24 hours"
    price = db.Column(db.Float)
    normal_range = db.Column(db.Text)
    instructions = db.Column(db.Text)  # Pre-test instructions
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_code': self.test_code,
            'test_name': self.test_name,
            'category': self.category,
            'sample_type': self.sample_type,
            'turnaround_time': self.turnaround_time,
            'price': self.price,
            'normal_range': self.normal_range
        }

class LabOrder(db.Model):
    """Lab test orders"""
    __tablename__ = 'lab_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    ordered_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.String(20), default='routine')  # routine, urgent, stat
    status = db.Column(db.Enum(LabTestStatus), default=LabTestStatus.ORDERED)
    clinical_notes = db.Column(db.Text)
    sample_collected_at = db.Column(db.DateTime)
    sample_collected_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed_at = db.Column(db.DateTime)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('LabOrderItem', backref='order', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'priority': self.priority,
            'status': self.status.value if self.status else None,
            'items': [item.to_dict() for item in self.items]
        }

class LabOrderItem(db.Model):
    """Individual tests in a lab order"""
    __tablename__ = 'lab_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('lab_orders.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('lab_tests.id'), nullable=False)
    result_value = db.Column(db.Text)
    result_unit = db.Column(db.String(50))
    normal_range = db.Column(db.String(100))
    is_abnormal = db.Column(db.Boolean, default=False)
    interpretation = db.Column(db.Text)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    test = db.relationship('LabTest')
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_name': self.test.test_name if self.test else None,
            'test_code': self.test.test_code if self.test else None,
            'result_value': self.result_value,
            'result_unit': self.result_unit,
            'normal_range': self.normal_range,
            'is_abnormal': self.is_abnormal,
            'interpretation': self.interpretation
        }

# ============== BILLING ==============

class Bill(db.Model):
    """Patient billing"""
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    admission_id = db.Column(db.Integer, db.ForeignKey('admissions.id'))
    bill_type = db.Column(db.String(20))  # OPD, IPD, Pharmacy, Lab
    bill_date = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Float, default=0)
    discount_percent = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    paid_amount = db.Column(db.Float, default=0)
    balance_amount = db.Column(db.Float, default=0)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = db.Column(db.String(50))  # Cash, Card, UPI, Insurance
    insurance_claim_id = db.Column(db.String(50))
    insurance_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('BillItem', backref='bill', lazy='dynamic')
    payments = db.relationship('Payment', backref='bill', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'bill_number': self.bill_number,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'bill_type': self.bill_type,
            'bill_date': self.bill_date.isoformat() if self.bill_date else None,
            'subtotal': self.subtotal,
            'discount_amount': self.discount_amount,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'paid_amount': self.paid_amount,
            'balance_amount': self.balance_amount,
            'payment_status': self.payment_status.value if self.payment_status else None,
            'items': [item.to_dict() for item in self.items]
        }

class BillItem(db.Model):
    """Individual items in a bill"""
    __tablename__ = 'bill_items'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    item_type = db.Column(db.String(50))  # Consultation, Medicine, Lab, Room, Procedure
    item_name = db.Column(db.String(200), nullable=False)
    item_code = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_type': self.item_type,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount': self.discount,
            'total': self.total
        }

class Payment(db.Model):
    """Payment transactions"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(20), unique=True, nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    received_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'bill_id': self.bill_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None
        }

# ============== IN-PATIENT (IPD) ==============

class Ward(db.Model):
    """Hospital wards"""
    __tablename__ = 'wards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ward_type = db.Column(db.String(50))  # General, ICU, NICU, Private, Semi-Private
    floor = db.Column(db.String(20))
    total_beds = db.Column(db.Integer)
    available_beds = db.Column(db.Integer)
    charge_per_day = db.Column(db.Float)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    beds = db.relationship('Bed', backref='ward', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ward_type': self.ward_type,
            'floor': self.floor,
            'total_beds': self.total_beds,
            'available_beds': self.available_beds,
            'charge_per_day': self.charge_per_day
        }

class Bed(db.Model):
    """Hospital beds"""
    __tablename__ = 'beds'
    
    id = db.Column(db.Integer, primary_key=True)
    bed_number = db.Column(db.String(20), nullable=False)
    ward_id = db.Column(db.Integer, db.ForeignKey('wards.id'), nullable=False)
    bed_type = db.Column(db.String(50))  # Regular, ICU, Ventilator
    is_occupied = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bed_number': self.bed_number,
            'ward_name': self.ward.name if self.ward else None,
            'bed_type': self.bed_type,
            'is_occupied': self.is_occupied
        }

class Admission(db.Model):
    """Patient admissions (IPD)"""
    __tablename__ = 'admissions'
    
    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    bed_id = db.Column(db.Integer, db.ForeignKey('beds.id'))
    admitting_doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    discharge_date = db.Column(db.DateTime)
    expected_discharge_date = db.Column(db.Date)
    admission_reason = db.Column(db.Text)
    admission_diagnosis = db.Column(db.Text)
    discharge_diagnosis = db.Column(db.Text)
    discharge_summary = db.Column(db.Text)
    status = db.Column(db.Enum(AdmissionStatus), default=AdmissionStatus.ADMITTED)
    
    # AI Agent Integration
    ai_length_of_stay_prediction = db.Column(db.Integer)  # From prediction agents
    ai_risk_score = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bed = db.relationship('Bed')
    admitting_doctor = db.relationship('User', foreign_keys=[admitting_doctor_id])
    
    def to_dict(self):
        return {
            'id': self.id,
            'admission_id': self.admission_id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.full_name if self.patient else None,
            'bed_number': self.bed.bed_number if self.bed else None,
            'ward_name': self.bed.ward.name if self.bed and self.bed.ward else None,
            'admitting_doctor': self.admitting_doctor.full_name if self.admitting_doctor else None,
            'admission_date': self.admission_date.isoformat() if self.admission_date else None,
            'discharge_date': self.discharge_date.isoformat() if self.discharge_date else None,
            'status': self.status.value if self.status else None,
            'admission_diagnosis': self.admission_diagnosis,
            'ai_length_of_stay_prediction': self.ai_length_of_stay_prediction
        }

# ============== INVENTORY ==============

class InventoryCategory(db.Model):
    """Inventory categories"""
    __tablename__ = 'inventory_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active
        }

class Supplier(db.Model):
    """Suppliers for inventory"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    gst_number = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'is_active': self.is_active
        }

class InventoryItem(db.Model):
    """General inventory items (non-medicine)"""
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(50), unique=True, nullable=False)
    sku = db.Column(db.String(50))
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_categories.id'))
    category = db.Column(db.String(100))  # Equipment, Consumables, Supplies
    description = db.Column(db.Text)
    unit = db.Column(db.String(20))
    current_stock = db.Column(db.Integer, default=0)
    quantity_in_stock = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    unit_price = db.Column(db.Float, default=0)
    unit_cost = db.Column(db.Float)
    expiry_date = db.Column(db.Date)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier = db.Column(db.String(200))
    location = db.Column(db.String(100))
    last_restocked = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_code': self.item_code,
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'current_stock': self.current_stock or self.quantity_in_stock,
            'quantity_in_stock': self.quantity_in_stock,
            'reorder_level': self.reorder_level,
            'unit_price': self.unit_price,
            'unit_cost': self.unit_cost,
            'is_low_stock': (self.current_stock or self.quantity_in_stock) <= self.reorder_level,
            'is_active': self.is_active
        }

class StockTransaction(db.Model):
    """Stock movement transactions"""
    __tablename__ = 'stock_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    transaction_type = db.Column(db.String(20))  # stock_in, stock_out, adjustment
    quantity = db.Column(db.Integer, nullable=False)
    old_quantity = db.Column(db.Integer)
    new_quantity = db.Column(db.Integer)
    reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('InventoryItem')
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'old_quantity': self.old_quantity,
            'new_quantity': self.new_quantity,
            'reference': self.reference,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PurchaseOrder(db.Model):
    """Purchase orders for inventory"""
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(20), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    items = db.Column(db.Text)  # JSON
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='draft')
    expected_delivery = db.Column(db.Date)
    received_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    supplier_rel = db.relationship('Supplier')
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'po_number': self.po_number,
            'supplier_id': self.supplier_id,
            'items': json.loads(self.items) if self.items else [],
            'total_amount': self.total_amount,
            'status': self.status,
            'expected_delivery': self.expected_delivery.isoformat() if self.expected_delivery else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============== NOTIFICATIONS ==============

class Notification(db.Model):
    """System notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # alert, reminder, info
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============== AUDIT LOG ==============

class AuditLog(db.Model):
    """System audit trail"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)  # JSON
    new_values = db.Column(db.Text)  # JSON
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============== HELPER FUNCTIONS ==============

def generate_id(prefix, model_class):
    """Generate unique IDs like PAT001, APT001, etc."""
    import random
    import string
    count = model_class.query.count() + 1
    return f"{prefix}{count:06d}"


def init_db(app):
    """Initialize database with sample data in app context"""
    from datetime import date
    
    with app.app_context():
        try:
            # Create sample patients
            patients_created = 0
            patient_ids = ['PAT001', 'PAT002', 'PAT003', 'PAT004', 'PAT005']
            patient_data = [
                ('John', 'Doe', date(1990, 5, 15), Gender.MALE, '9999999999', 'john@example.com', 'O+', '123 Main St', 'City', 'State', 'Jane Doe', '9999999998'),
                ('Mary', 'Smith', date(1985, 8, 22), Gender.FEMALE, '9999999997', 'mary@example.com', 'B+', '456 Oak St', 'City', 'State', 'Robert Smith', '9999999996'),
                ('Robert', 'Johnson', date(1978, 3, 10), Gender.MALE, '9999999995', 'robert@example.com', 'A+', '789 Pine St', 'City', 'State', 'Sarah Johnson', '9999999994'),
                ('Sarah', 'Williams', date(1992, 11, 18), Gender.FEMALE, '9999999993', 'sarah@example.com', 'AB+', '321 Elm St', 'City', 'State', 'Michael Williams', '9999999992'),
                ('Michael', 'Brown', date(1988, 6, 7), Gender.MALE, '9999999991', 'michael@example.com', 'O-', '654 Maple St', 'City', 'State', 'Lisa Brown', '9999999990'),
            ]
            
            for pat_id, (first, last, dob, gender, phone, email, blood, addr, city, state, emer_name, emer_phone) in zip(patient_ids, patient_data):
                if not Patient.query.filter_by(patient_id=pat_id).first():
                    patients_created += 1
                    patient = Patient(
                        patient_id=pat_id,
                        first_name=first,
                        last_name=last,
                        date_of_birth=dob,
                        gender=gender,
                        phone=phone,
                        email=email,
                        blood_group=blood,
                        address=addr,
                        city=city,
                        state=state,
                        emergency_contact_name=emer_name,
                        emergency_contact_phone=emer_phone,
                        is_active=True
                    )
                    db.session.add(patient)
            
            if patients_created > 0:
                db.session.commit()
                print(f"✓ Created {patients_created} sample patients")
        
        except Exception as e:
            print(f"✗ Sample patients error: {str(e)}")
            db.session.rollback()
