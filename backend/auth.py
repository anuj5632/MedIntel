"""
Authentication Module for MedIntel Hospital Management System
JWT-based authentication with role-based access control
"""

from functools import wraps
from datetime import datetime, timedelta
import jwt
from flask import Blueprint, request, jsonify, current_app
from models import db, User, UserRole, AuditLog

auth_bp = Blueprint('auth', __name__)

def generate_token(user, expires_hours=24):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role.value,
        'exp': datetime.utcnow() + timedelta(hours=expires_hours),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user from database
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        # Add user to request context
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated

def role_required(*roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = request.current_user.role
            allowed_roles = [UserRole(r) if isinstance(r, str) else r for r in roles]
            
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def log_action(action, entity_type=None, entity_id=None, old_values=None, new_values=None):
    """Log user action for audit trail"""
    try:
        user_id = request.current_user.id if hasattr(request, 'current_user') else None
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=str(old_values) if old_values else None,
            new_values=str(new_values) if new_values else None,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:255] if request.user_agent else None
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging action: {e}")


# ============== AUTH ROUTES ==============

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (admin only in production)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password', 'first_name', 'last_name']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            role=UserRole(data.get('role', 'receptionist')),
            department=data.get('department'),
            specialization=data.get('specialization'),
            license_number=data.get('license_number'),
            is_active=True
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        log_action('user_registered', 'user', user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(user)
        
        log_action('user_login', 'user', user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current logged in user"""
    return jsonify({
        'user': request.current_user.to_dict()
    })

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        user = request.current_user
        
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        log_action('password_changed', 'user', user.id)
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin')
def list_users():
    """List all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [u.to_dict() for u in users]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        old_values = user.to_dict()
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'role' in data:
            user.role = UserRole(data['role'])
        if 'department' in data:
            user.department = data['department']
        if 'specialization' in data:
            user.specialization = data['specialization']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        log_action('user_updated', 'user', user.id, old_values, user.to_dict())
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(user_id):
    """Deactivate user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        
        if user.id == request.current_user.id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        user.is_active = False
        db.session.commit()
        
        log_action('user_deactivated', 'user', user.id)
        
        return jsonify({'message': 'User deactivated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/doctors', methods=['GET'])
@token_required
def list_doctors():
    """List all active doctors"""
    try:
        doctors = User.query.filter_by(role=UserRole.DOCTOR, is_active=True).all()
        return jsonify({
            'doctors': [d.to_dict() for d in doctors]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
