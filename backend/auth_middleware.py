from functools import wraps
from flask import request, jsonify, current_app
import jwt
from database.models import User
from database import db

def token_required(f):
    """
    Decorator to protect routes that require authentication.
    Validates JWT token and passes the current user to the route.
    
    Usage:
    @token_required
    def protected_route(current_user):
        # current_user is the authenticated User object
        return jsonify({'message': f'Hello {current_user.username}'})
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        #get token from auth header
        auth_header = request.headers.get('Authorization', None)

        if auth_header:
            try:
                # Expecting header format: "Bearer <token>"
                token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
            except IndexError:
                return jsonify({'error': 'Token format is invalid'}), 401
            
        if not token:
            return jsonify({'error': 'Auth token is missing'}), 401
        
        try:
            #decode and validate token
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )

            #get user from db
            user_id = payload['user_id']
            current_user = db.session.get(User, user_id) 

            if not current_user:
                return jsonify({'error': 'User not found'}), 404
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            current_app.logger.error(f"Token validation error: {e}")
            return jsonify({'error': 'Token validation failed'}), 401
        
        #pass current_user to the route
        return f(current_user, *args, **kwargs)
    
    return decorated

def optional_token(f):
    """
    Decorator for routes where authentication is optional.
    If token is provided and valid, current_user is passed, otherwise None.
    
    Usage:
    @optional_token
    def public_route(current_user=None):
        if current_user:
            return jsonify({'message': f'Hello {current_user.username}'})
        return jsonify({'message': 'Hello guest'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        current_user = None
        
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
                
                payload = jwt.decode(
                    token,
                    current_app.config['SECRET_KEY'],
                    algorithms=['HS256']
                )
                
                user_id = payload['user_id']
                current_user = db.session.get(User, user_id)  
                
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception):
                #token invalid or expired, but route continues with current_user=None
                pass
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def verify_token(token):
    """
    Utility function to verify a token without using a decorator.
    Returns user if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        user_id = payload['user_id']
        return db.session.get(User, user_id) 
    except Exception:
        return None

