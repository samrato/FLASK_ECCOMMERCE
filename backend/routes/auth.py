from flask import request, jsonify,Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from backend import db
from backend.models.user import User, UserSchema
from backend.services.auth import AuthService
from backend.utils.decorators import validate_schema
from backend.utils.validators import validate_email,validate_password
from backend.routes import auth_bp

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@auth_bp.route('/register', methods=['POST'])
@validate_schema(user_schema)
def register():
    data = request.get_json()
    #requestinng data 
    password = request.json.get('password')
    is_valid_password, error = validate_password(data['password'])
    if not is_valid_password:
        return jsonify({'message': error}), 400
    if not validate_email(data['email']):
        return jsonify({'message': 'Invalid email format'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    
    return user_schema.jsonify(user), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    access_token, refresh_token = user.generate_auth_tokens()
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user_schema.dump(user)
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = int(get_jwt_identity())
    new_token = create_access_token(identity=current_user)
    return jsonify({'access_token': new_token}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Email not found'}), 404
    
    # Generate reset token and send email
    reset_token = AuthService.generate_reset_token(user)
    AuthService.send_reset_email(user.email, reset_token)
    
    return jsonify({'message': 'Password reset email sent'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    password = request.json.get('password')
    is_valid, error = validate_password(password)
    if not is_valid:
        return jsonify({'message': error}), 400
    
    user = AuthService.verify_reset_token(token)
    if not user:
        return jsonify({'message': 'Invalid or expired token'}), 400
    
    user.set_password(password)
    db.session.commit()
    
    return jsonify({'message': 'Password updated successfully'}), 200