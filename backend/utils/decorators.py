from functools import wraps
from flask import jsonify,request
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return jsonify({'message': 'Admins only'}), 403
        return fn(*args, **kwargs)
    return wrapper

def seller_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get('is_seller', False):
            return jsonify({'message': 'Sellers only'}), 403
        return fn(*args, **kwargs)
    return wrapper

def validate_schema(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            errors = schema.validate(request.get_json())
            if errors:
                return jsonify({'errors': errors}), 400
            return fn(*args, **kwargs)
        return wrapper
    return decorator