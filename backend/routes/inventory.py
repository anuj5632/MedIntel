"""
Inventory & Stock Management Module for MedIntel Hospital Management System
Equipment tracking, stock management, procurement
"""

from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify
from models import (
    db, InventoryItem, InventoryCategory, StockTransaction,
    Supplier, PurchaseOrder, generate_id
)
from auth import token_required, role_required, log_action

inventory_bp = Blueprint('inventory', __name__)

# ============== CATEGORIES ==============

@inventory_bp.route('/categories', methods=['GET'])
@token_required
def list_categories():
    """List all inventory categories"""
    try:
        categories = InventoryCategory.query.filter_by(is_active=True).all()
        return jsonify({'categories': [c.to_dict() for c in categories]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/categories', methods=['POST'])
@token_required
@role_required('admin', 'inventory_manager')
def create_category():
    """Create inventory category"""
    try:
        data = request.get_json()
        
        category = InventoryCategory(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== INVENTORY ITEMS ==============

@inventory_bp.route('/items', methods=['GET'])
@token_required
def list_items():
    """List inventory items with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search', '')
        low_stock = request.args.get('low_stock', type=bool)
        
        query = InventoryItem.query.filter_by(is_active=True)
        
        if category_id:
            query = query.filter(InventoryItem.category_id == category_id)
        
        if search:
            query = query.filter(
                db.or_(
                    InventoryItem.name.ilike(f'%{search}%'),
                    InventoryItem.sku.ilike(f'%{search}%')
                )
            )
        
        if low_stock:
            query = query.filter(InventoryItem.current_stock <= InventoryItem.reorder_level)
        
        items = query.order_by(InventoryItem.name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'items': [i.to_dict() for i in items.items],
            'total': items.total,
            'pages': items.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items', methods=['POST'])
@token_required
@role_required('admin', 'inventory_manager')
def create_item():
    """Create new inventory item"""
    try:
        data = request.get_json()
        
        sku = data.get('sku') or generate_id('INV', InventoryItem)
        
        item = InventoryItem(
            sku=sku,
            name=data['name'],
            category_id=data.get('category_id'),
            description=data.get('description'),
            unit=data.get('unit', 'pcs'),
            current_stock=data.get('current_stock', 0),
            reorder_level=data.get('reorder_level', 10),
            unit_price=data.get('unit_price', 0),
            location=data.get('location'),
            supplier_id=data.get('supplier_id')
        )
        
        if data.get('expiry_date'):
            item.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        
        db.session.add(item)
        db.session.commit()
        
        log_action('inventory_item_created', 'inventory', item.id)
        
        return jsonify({
            'message': 'Item created successfully',
            'item': item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items/<int:item_id>', methods=['GET'])
@token_required
def get_item(item_id):
    """Get item details"""
    try:
        item = InventoryItem.query.get_or_404(item_id)
        return jsonify({'item': item.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items/<int:item_id>', methods=['PUT'])
@token_required
@role_required('admin', 'inventory_manager')
def update_item(item_id):
    """Update inventory item"""
    try:
        item = InventoryItem.query.get_or_404(item_id)
        data = request.get_json()
        
        for field in ['name', 'description', 'unit', 'reorder_level', 
                      'unit_price', 'location', 'supplier_id', 'category_id']:
            if field in data:
                setattr(item, field, data[field])
        
        if 'expiry_date' in data:
            item.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data['expiry_date'] else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Item updated successfully',
            'item': item.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== STOCK TRANSACTIONS ==============

@inventory_bp.route('/transactions', methods=['GET'])
@token_required
def list_transactions():
    """List stock transactions"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        item_id = request.args.get('item_id', type=int)
        transaction_type = request.args.get('type')
        
        query = StockTransaction.query
        
        if item_id:
            query = query.filter(StockTransaction.item_id == item_id)
        
        if transaction_type:
            query = query.filter(StockTransaction.transaction_type == transaction_type)
        
        transactions = query.order_by(StockTransaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/stock-in', methods=['POST'])
@token_required
@role_required('admin', 'inventory_manager')
def stock_in():
    """Add stock (stock in)"""
    try:
        data = request.get_json()
        
        item = InventoryItem.query.get(data.get('item_id'))
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        quantity = data.get('quantity', 0)
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        # Update stock
        old_stock = item.current_stock
        item.current_stock += quantity
        
        # Create transaction
        transaction = StockTransaction(
            item_id=item.id,
            transaction_type='stock_in',
            quantity=quantity,
            old_quantity=old_stock,
            new_quantity=item.current_stock,
            reference=data.get('reference'),
            notes=data.get('notes')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        log_action('stock_in', 'inventory', item.id)
        
        return jsonify({
            'message': f'Stock added. New quantity: {item.current_stock}',
            'item': item.to_dict(),
            'transaction': transaction.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/stock-out', methods=['POST'])
@token_required
@role_required('admin', 'inventory_manager', 'nurse')
def stock_out():
    """Remove stock (stock out)"""
    try:
        data = request.get_json()
        
        item = InventoryItem.query.get(data.get('item_id'))
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        quantity = data.get('quantity', 0)
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        if item.current_stock < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Update stock
        old_stock = item.current_stock
        item.current_stock -= quantity
        
        # Create transaction
        transaction = StockTransaction(
            item_id=item.id,
            transaction_type='stock_out',
            quantity=-quantity,
            old_quantity=old_stock,
            new_quantity=item.current_stock,
            reference=data.get('reference'),
            notes=data.get('notes')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        log_action('stock_out', 'inventory', item.id)
        
        return jsonify({
            'message': f'Stock removed. New quantity: {item.current_stock}',
            'item': item.to_dict(),
            'transaction': transaction.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== SUPPLIERS ==============

@inventory_bp.route('/suppliers', methods=['GET'])
@token_required
def list_suppliers():
    """List all suppliers"""
    try:
        suppliers = Supplier.query.filter_by(is_active=True).all()
        return jsonify({'suppliers': [s.to_dict() for s in suppliers]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/suppliers', methods=['POST'])
@token_required
@role_required('admin', 'inventory_manager')
def create_supplier():
    """Create new supplier"""
    try:
        data = request.get_json()
        
        supplier = Supplier(
            name=data['name'],
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            gst_number=data.get('gst_number')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return jsonify({
            'message': 'Supplier created',
            'supplier': supplier.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== PURCHASE ORDERS ==============

@inventory_bp.route('/purchase-orders', methods=['GET'])
@token_required
def list_purchase_orders():
    """List purchase orders"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        query = PurchaseOrder.query
        
        if status:
            query = query.filter(PurchaseOrder.status == status)
        
        orders = query.order_by(PurchaseOrder.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'orders': [o.to_dict() for o in orders.items],
            'total': orders.total,
            'pages': orders.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/purchase-orders', methods=['POST'])
@token_required
@role_required('admin', 'inventory_manager')
def create_purchase_order():
    """Create purchase order"""
    try:
        data = request.get_json()
        
        po_number = generate_id('PO', PurchaseOrder)
        
        order = PurchaseOrder(
            po_number=po_number,
            supplier_id=data['supplier_id'],
            items=data.get('items', []),
            total_amount=data.get('total_amount', 0),
            status='draft',
            notes=data.get('notes')
        )
        
        if data.get('expected_delivery'):
            order.expected_delivery = datetime.strptime(
                data['expected_delivery'], '%Y-%m-%d'
            ).date()
        
        db.session.add(order)
        db.session.commit()
        
        log_action('purchase_order_created', 'purchase_order', order.id)
        
        return jsonify({
            'message': 'Purchase order created',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== ALERTS & REPORTS ==============

@inventory_bp.route('/alerts', methods=['GET'])
@token_required
def get_alerts():
    """Get inventory alerts"""
    try:
        # Low stock items
        low_stock = InventoryItem.query.filter(
            InventoryItem.is_active == True,
            InventoryItem.current_stock <= InventoryItem.reorder_level
        ).all()
        
        # Expiring items (within 30 days)
        expiry_threshold = date.today() + timedelta(days=30)
        expiring = InventoryItem.query.filter(
            InventoryItem.is_active == True,
            InventoryItem.expiry_date != None,
            InventoryItem.expiry_date <= expiry_threshold,
            InventoryItem.current_stock > 0
        ).all()
        
        # Expired items
        expired = InventoryItem.query.filter(
            InventoryItem.is_active == True,
            InventoryItem.expiry_date != None,
            InventoryItem.expiry_date < date.today(),
            InventoryItem.current_stock > 0
        ).all()
        
        return jsonify({
            'low_stock': [i.to_dict() for i in low_stock],
            'expiring_soon': [i.to_dict() for i in expiring],
            'expired': [i.to_dict() for i in expired],
            'alerts_count': {
                'low_stock': len(low_stock),
                'expiring': len(expiring),
                'expired': len(expired)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/stats', methods=['GET'])
@token_required
def inventory_stats():
    """Get inventory statistics"""
    try:
        total_items = InventoryItem.query.filter_by(is_active=True).count()
        
        total_value = db.session.query(
            db.func.sum(InventoryItem.current_stock * InventoryItem.unit_price)
        ).filter(InventoryItem.is_active == True).scalar() or 0
        
        low_stock_count = InventoryItem.query.filter(
            InventoryItem.is_active == True,
            InventoryItem.current_stock <= InventoryItem.reorder_level
        ).count()
        
        out_of_stock = InventoryItem.query.filter(
            InventoryItem.is_active == True,
            InventoryItem.current_stock == 0
        ).count()
        
        # Category breakdown
        categories = InventoryCategory.query.filter_by(is_active=True).all()
        category_stats = []
        for cat in categories:
            count = InventoryItem.query.filter_by(
                category_id=cat.id, is_active=True
            ).count()
            category_stats.append({
                'name': cat.name,
                'item_count': count
            })
        
        return jsonify({
            'total_items': total_items,
            'total_value': float(total_value),
            'low_stock_count': low_stock_count,
            'out_of_stock': out_of_stock,
            'categories': category_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
