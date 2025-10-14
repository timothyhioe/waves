from flask import Blueprint, request, jsonify, current_app
from database.models import User, db
from datetime import datetime, timezone
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format (alphanumeric, underscore, hyphen, 3-20 chars)"""
    pattern = r'^[a-zA-Z0-9_-]{3,20}$'
    return re.match(pattern, username) is not None

def validate_password(password):
    """Validate password strength (min 8 chars, at least one letter and one number)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Valid"

#registration endpoint
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    try:
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not username:
            return jsonify({'error': 'Username is required'}), 400
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        #validate username format
        if not validate_username(username):
            return jsonify({'error': 'Username must be 3-20 characters long and contain only letters, numbers, underscores, or hyphens.'}), 400
        
        #validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        #validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        #check if username or email already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        #create new user
        new_user = User(
            username=username,
            email=email
        )
        new_user.set_password(password)

        #save to database
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
            }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {e}")
        return jsonify({'error': str(e)}), 500
    

#username and email availability check endpoints
@auth_bp.route('/check-username/<username>', methods=['GET'])
def check_username(username):
    user = User.query.filter_by(username=username).first()
    return jsonify({
        'available': user is None,
        'username': username
    }), 200

@auth_bp.route('/check-email/<email>', methods=['GET'])
def check_email(email):
    user = User.query.filter_by(email=email).first()
    return jsonify({
        'available': user is None,
        'email': email
    }), 200