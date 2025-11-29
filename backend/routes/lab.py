"""
Laboratory Module for MedIntel Hospital Management System
Lab tests, orders, results, reporting
"""

from datetime import datetime, date
from flask import Blueprint, request, jsonify
from models import (
    db, LabTest, LabOrder, LabOrderItem, Patient,
    LabTestStatus, generate_id
)
from auth import token_required, role_required, log_action

lab_bp = Blueprint('lab', __name__)

# ============== LAB TESTS CATALOG ==============

@lab_bp.route('/tests', methods=['GET'])
@token_required
def list_tests():
    """List all available lab tests"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category')
        
        query = LabTest.query.filter_by(is_active=True)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    LabTest.test_name.ilike(search_filter),
                    LabTest.test_code.ilike(search_filter)
                )
            )
        
        if category:
            query = query.filter(LabTest.category == category)
        
        tests = query.order_by(LabTest.test_name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'tests': [t.to_dict() for t in tests.items],
            'total': tests.total,
            'pages': tests.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/tests', methods=['POST'])
@token_required
@role_required('admin', 'lab_tech')
def add_test():
    """Add a new lab test to catalog"""
    try:
        data = request.get_json()
        
        test = LabTest(
            test_code=data['test_code'],
            test_name=data['test_name'],
            category=data.get('category'),
            sample_type=data.get('sample_type'),
            sample_volume=data.get('sample_volume'),
            container_type=data.get('container_type'),
            turnaround_time=data.get('turnaround_time'),
            price=data.get('price'),
            normal_range=data.get('normal_range'),
            instructions=data.get('instructions')
        )
        
        db.session.add(test)
        db.session.commit()
        
        log_action('lab_test_added', 'lab_test', test.id)
        
        return jsonify({
            'message': 'Lab test added successfully',
            'test': test.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/tests/categories', methods=['GET'])
@token_required
def get_test_categories():
    """Get all test categories"""
    try:
        categories = db.session.query(LabTest.category).filter(
            LabTest.is_active == True,
            LabTest.category.isnot(None)
        ).distinct().all()
        
        return jsonify({
            'categories': [c[0] for c in categories]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== LAB ORDERS ==============

@lab_bp.route('/orders', methods=['GET'])
@token_required
def list_orders():
    """List lab orders"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        patient_id = request.args.get('patient_id', type=int)
        status = request.args.get('status')
        priority = request.args.get('priority')
        date_filter = request.args.get('date')
        
        query = LabOrder.query
        
        if patient_id:
            query = query.filter(LabOrder.patient_id == patient_id)
        
        if status:
            query = query.filter(LabOrder.status == LabTestStatus(status))
        
        if priority:
            query = query.filter(LabOrder.priority == priority)
        
        if date_filter:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(LabOrder.order_date) == filter_date)
        
        orders = query.order_by(LabOrder.order_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'orders': [o.to_dict() for o in orders.items],
            'total': orders.total,
            'pages': orders.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/orders', methods=['POST'])
@token_required
@role_required('doctor', 'admin', 'lab_tech')
def create_order():
    """Create a new lab order"""
    try:
        data = request.get_json()
        
        # Validate patient
        patient = Patient.query.get(data.get('patient_id'))
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        order_id = generate_id('LAB', LabOrder)
        
        order = LabOrder(
            order_id=order_id,
            patient_id=data['patient_id'],
            ordered_by=request.current_user.id,
            appointment_id=data.get('appointment_id'),
            priority=data.get('priority', 'routine'),
            clinical_notes=data.get('clinical_notes'),
            status=LabTestStatus.ORDERED
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Add test items
        for test_id in data.get('test_ids', []):
            test = LabTest.query.get(test_id)
            if test:
                item = LabOrderItem(
                    order_id=order.id,
                    test_id=test_id,
                    normal_range=test.normal_range
                )
                db.session.add(item)
        
        db.session.commit()
        
        log_action('lab_order_created', 'lab_order', order.id)
        
        return jsonify({
            'message': 'Lab order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """Get lab order details"""
    try:
        order = LabOrder.query.get_or_404(order_id)
        
        order_data = order.to_dict()
        order_data['items'] = [item.to_dict() for item in order.items]
        
        return jsonify({'order': order_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/orders/<int:order_id>/collect-sample', methods=['POST'])
@token_required
@role_required('lab_tech', 'nurse', 'admin')
def collect_sample(order_id):
    """Mark sample as collected"""
    try:
        order = LabOrder.query.get_or_404(order_id)
        
        order.status = LabTestStatus.SAMPLE_COLLECTED
        order.sample_collected_at = datetime.utcnow()
        order.sample_collected_by = request.current_user.id
        
        db.session.commit()
        
        log_action('sample_collected', 'lab_order', order.id)
        
        return jsonify({
            'message': 'Sample collected successfully',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/orders/<int:order_id>/start-processing', methods=['POST'])
@token_required
@role_required('lab_tech', 'admin')
def start_processing(order_id):
    """Start processing lab order"""
    try:
        order = LabOrder.query.get_or_404(order_id)
        
        order.status = LabTestStatus.IN_PROGRESS
        
        db.session.commit()
        
        return jsonify({
            'message': 'Processing started',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/orders/<int:order_id>/results', methods=['POST'])
@token_required
@role_required('lab_tech', 'admin')
def enter_results(order_id):
    """Enter lab test results"""
    try:
        order = LabOrder.query.get_or_404(order_id)
        data = request.get_json()
        
        # Update results for each item
        for result_data in data.get('results', []):
            item = LabOrderItem.query.get(result_data['item_id'])
            if item and item.order_id == order.id:
                item.result_value = result_data.get('result_value')
                item.result_unit = result_data.get('result_unit')
                item.is_abnormal = result_data.get('is_abnormal', False)
                item.interpretation = result_data.get('interpretation')
                item.completed_at = datetime.utcnow()
        
        # Check if all items have results
        all_completed = all(item.result_value for item in order.items)
        
        if all_completed:
            order.status = LabTestStatus.COMPLETED
            order.completed_at = datetime.utcnow()
            order.reported_by = request.current_user.id
        
        db.session.commit()
        
        log_action('lab_results_entered', 'lab_order', order.id)
        
        return jsonify({
            'message': 'Results entered successfully',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/orders/<int:order_id>/deliver', methods=['POST'])
@token_required
@role_required('lab_tech', 'admin')
def deliver_results(order_id):
    """Mark results as delivered"""
    try:
        order = LabOrder.query.get_or_404(order_id)
        
        if order.status != LabTestStatus.COMPLETED:
            return jsonify({'error': 'Results not yet completed'}), 400
        
        order.status = LabTestStatus.DELIVERED
        
        db.session.commit()
        
        return jsonify({
            'message': 'Results delivered',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== LAB STATISTICS ==============

@lab_bp.route('/stats', methods=['GET'])
@token_required
def lab_statistics():
    """Get lab statistics"""
    try:
        today = date.today()
        
        # Today's orders
        today_orders = LabOrder.query.filter(
            db.func.date(LabOrder.order_date) == today
        ).count()
        
        # Pending samples
        pending_samples = LabOrder.query.filter(
            LabOrder.status == LabTestStatus.ORDERED
        ).count()
        
        # In progress
        in_progress = LabOrder.query.filter(
            LabOrder.status.in_([LabTestStatus.SAMPLE_COLLECTED, LabTestStatus.IN_PROGRESS])
        ).count()
        
        # Completed today
        completed_today = LabOrder.query.filter(
            LabOrder.status == LabTestStatus.COMPLETED,
            db.func.date(LabOrder.completed_at) == today
        ).count()
        
        # Urgent pending
        urgent_pending = LabOrder.query.filter(
            LabOrder.priority.in_(['urgent', 'stat']),
            LabOrder.status.notin_([LabTestStatus.COMPLETED, LabTestStatus.DELIVERED])
        ).count()
        
        return jsonify({
            'today_orders': today_orders,
            'pending_samples': pending_samples,
            'in_progress': in_progress,
            'completed_today': completed_today,
            'urgent_pending': urgent_pending
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lab_bp.route('/pending', methods=['GET'])
@token_required
def get_pending_orders():
    """Get pending lab orders for worklist"""
    try:
        orders = LabOrder.query.filter(
            LabOrder.status.notin_([LabTestStatus.COMPLETED, LabTestStatus.DELIVERED])
        ).order_by(
            # Prioritize urgent orders
            db.case(
                (LabOrder.priority == 'stat', 1),
                (LabOrder.priority == 'urgent', 2),
                else_=3
            ),
            LabOrder.order_date.asc()
        ).all()
        
        return jsonify({
            'orders': [o.to_dict() for o in orders]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
