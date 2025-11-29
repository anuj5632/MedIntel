"""
Billing Module for MedIntel Hospital Management System
OPD/IPD billing, invoices, payments
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify
from models import (
    db, Bill, BillItem, Payment, Patient,
    PaymentStatus, generate_id
)
from auth import token_required, role_required, log_action

billing_bp = Blueprint('billing', __name__)

# ============== BILLS ==============

@billing_bp.route('', methods=['GET'])
@token_required
def list_bills():
    """List all bills with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filters
        patient_id = request.args.get('patient_id', type=int)
        status = request.args.get('status')
        bill_type = request.args.get('bill_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Bill.query
        
        if patient_id:
            query = query.filter(Bill.patient_id == patient_id)
        
        if status:
            query = query.filter(Bill.payment_status == PaymentStatus(status))
        
        if bill_type:
            query = query.filter(Bill.bill_type == bill_type)
        
        if date_from:
            query = query.filter(Bill.bill_date >= datetime.strptime(date_from, '%Y-%m-%d'))
        
        if date_to:
            query = query.filter(Bill.bill_date <= datetime.strptime(date_to, '%Y-%m-%d'))
        
        bills = query.order_by(Bill.bill_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'bills': [b.to_dict() for b in bills.items],
            'total': bills.total,
            'pages': bills.pages,
            'current_page': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@billing_bp.route('', methods=['POST'])
@token_required
def create_bill():
    """Create a new bill"""
    try:
        data = request.get_json()
        
        # Validate patient
        patient = Patient.query.get(data.get('patient_id'))
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        # Generate bill number
        bill_number = generate_id('BILL', Bill)
        
        # Create bill
        bill = Bill(
            bill_number=bill_number,
            patient_id=data['patient_id'],
            appointment_id=data.get('appointment_id'),
            admission_id=data.get('admission_id'),
            bill_type=data.get('bill_type', 'OPD'),
            discount_percent=data.get('discount_percent', 0),
            notes=data.get('notes'),
            created_by=request.current_user.id
        )
        
        db.session.add(bill)
        db.session.flush()  # Get bill ID
        
        # Add bill items
        subtotal = 0
        for item_data in data.get('items', []):
            item_total = item_data['quantity'] * item_data['unit_price']
            item_discount = item_data.get('discount', 0)
            item_tax = item_data.get('tax', 0)
            item_final = item_total - item_discount + item_tax
            
            item = BillItem(
                bill_id=bill.id,
                item_type=item_data.get('item_type'),
                item_name=item_data['item_name'],
                item_code=item_data.get('item_code'),
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                discount=item_discount,
                tax=item_tax,
                total=item_final
            )
            db.session.add(item)
            subtotal += item_final
        
        # Calculate totals
        bill.subtotal = subtotal
        bill.discount_amount = (subtotal * bill.discount_percent / 100) if bill.discount_percent else 0
        bill.tax_amount = data.get('tax_amount', 0)
        bill.total_amount = subtotal - bill.discount_amount + bill.tax_amount
        bill.balance_amount = bill.total_amount
        
        db.session.commit()
        
        log_action('bill_created', 'bill', bill.id)
        
        return jsonify({
            'message': 'Bill created successfully',
            'bill': bill.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/<int:bill_id>', methods=['GET'])
@token_required
def get_bill(bill_id):
    """Get bill details"""
    try:
        bill = Bill.query.get_or_404(bill_id)
        
        bill_data = bill.to_dict()
        bill_data['payments'] = [p.to_dict() for p in bill.payments]
        
        return jsonify({'bill': bill_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== PAYMENTS ==============

@billing_bp.route('/<int:bill_id>/pay', methods=['POST'])
@token_required
def record_payment(bill_id):
    """Record a payment for a bill"""
    try:
        bill = Bill.query.get_or_404(bill_id)
        data = request.get_json()
        
        amount = data.get('amount', 0)
        
        if amount <= 0:
            return jsonify({'error': 'Invalid payment amount'}), 400
        
        if amount > bill.balance_amount:
            return jsonify({'error': 'Payment amount exceeds balance'}), 400
        
        # Create payment record
        payment_id = generate_id('PAY', Payment)
        
        payment = Payment(
            payment_id=payment_id,
            bill_id=bill_id,
            amount=amount,
            payment_method=data.get('payment_method', 'cash'),
            transaction_id=data.get('transaction_id'),
            received_by=request.current_user.id,
            notes=data.get('notes')
        )
        
        db.session.add(payment)
        
        # Update bill
        bill.paid_amount += amount
        bill.balance_amount = bill.total_amount - bill.paid_amount
        
        if bill.balance_amount <= 0:
            bill.payment_status = PaymentStatus.PAID
        elif bill.paid_amount > 0:
            bill.payment_status = PaymentStatus.PARTIAL
        
        bill.payment_method = data.get('payment_method')
        
        db.session.commit()
        
        log_action('payment_recorded', 'payment', payment.id)
        
        return jsonify({
            'message': 'Payment recorded successfully',
            'payment': payment.to_dict(),
            'bill': bill.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== BILLING STATISTICS ==============

@billing_bp.route('/stats', methods=['GET'])
@token_required
def billing_statistics():
    """Get billing statistics"""
    try:
        today = date.today()
        start_of_month = today.replace(day=1)
        
        # Today's revenue
        today_revenue = db.session.query(
            db.func.sum(Bill.paid_amount)
        ).filter(
            db.func.date(Bill.bill_date) == today
        ).scalar() or 0
        
        # Month's revenue
        month_revenue = db.session.query(
            db.func.sum(Bill.paid_amount)
        ).filter(
            Bill.bill_date >= start_of_month
        ).scalar() or 0
        
        # Pending amount
        pending_amount = db.session.query(
            db.func.sum(Bill.balance_amount)
        ).filter(
            Bill.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL])
        ).scalar() or 0
        
        # Bills count today
        today_bills = Bill.query.filter(
            db.func.date(Bill.bill_date) == today
        ).count()
        
        # Payment method breakdown
        payment_breakdown = db.session.query(
            Payment.payment_method,
            db.func.sum(Payment.amount)
        ).filter(
            db.func.date(Payment.payment_date) == today
        ).group_by(Payment.payment_method).all()
        
        return jsonify({
            'today': {
                'revenue': float(today_revenue),
                'bills_count': today_bills
            },
            'this_month': {
                'revenue': float(month_revenue)
            },
            'pending_amount': float(pending_amount),
            'payment_methods': {method: float(amount) for method, amount in payment_breakdown if method}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== BILL TYPES ==============

@billing_bp.route('/generate-opd', methods=['POST'])
@token_required
def generate_opd_bill():
    """Generate OPD consultation bill"""
    try:
        data = request.get_json()
        
        # Auto-generate bill items for OPD
        items = [
            {
                'item_type': 'Consultation',
                'item_name': f"Consultation - {data.get('doctor_name', 'Doctor')}",
                'quantity': 1,
                'unit_price': data.get('consultation_fee', 500)
            }
        ]
        
        # Add any additional items
        items.extend(data.get('additional_items', []))
        
        data['items'] = items
        data['bill_type'] = 'OPD'
        
        # Call main create_bill logic
        return create_bill()
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
