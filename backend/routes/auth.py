from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import User
from extensions import mongo, mail
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate input
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.get_by_email(mongo, data['email']):
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User.create(
        mongo,
        data['username'],
        data['email'],
        data['password']
    )

    # Set verification token
    token = secrets.token_urlsafe()
    user.set_verification_token(mongo, token)
    
    # Send verification email
    verification_url = f"{request.url_root}auth/verify-email/{token}"
    mail.send_message(
        'Verify your email',
        sender='your-email@gmail.com',
        recipients=[user.email],
        body=f'Please click on the following link to verify your email: {verification_url}'
    )
    
    # Generate access token
    access_token = create_access_token(identity=str(user._id))
    
    return jsonify({
        'message': 'Registration successful. Please check your email to verify your account.',
        'access_token': access_token
    }), 201

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user's email."""
    email = User.get_email_from_verification_token(mongo, token)
    if not email:
        return jsonify({'error': 'Invalid or expired verification token'}), 400
    
    user = User.get_by_email(mongo, email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.is_verified:
        return jsonify({'message': 'Email already verified'})
    
    user.verify_email(mongo)
    return jsonify({'message': 'Email verified successfully'})

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.get_by_email(mongo, data['email'])
    if not user or not user.verify_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_verified:
        return jsonify({'error': 'Please verify your email before logging in'}), 401
    
    access_token = create_access_token(identity=str(user._id))
    return jsonify({'access_token': access_token})

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email."""
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.get_by_email(mongo, data['email'])
    if not user:
        # Don't reveal if email exists
        return jsonify({'message': 'If your email is registered, you will receive a password reset link'})
    
    # Generate reset token
    token = secrets.token_urlsafe()
    expires = datetime.utcnow() + timedelta(hours=1)
    user.set_reset_token(mongo, token, expires)
    
    # Send reset email
    reset_url = f"{request.url_root}auth/reset-password/{token}"
    mail.send_message(
        'Reset your password',
        sender='your-email@gmail.com',
        recipients=[user.email],
        body=f'Please click on the following link to reset your password: {reset_url}'
    )
    
    return jsonify({'message': 'If your email is registered, you will receive a password reset link'})

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset password using token."""
    data = request.get_json()
    
    if 'password' not in data:
        return jsonify({'error': 'New password is required'}), 400
    
    email = User.get_email_from_reset_token(mongo, token)
    if not email:
        return jsonify({'error': 'Invalid or expired reset token'}), 400
    
    user = User.get_by_email(mongo, email)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.reset_token or user.reset_token != token:
        return jsonify({'error': 'Invalid reset token'}), 400
    
    if user.reset_token_expires < datetime.utcnow():
        return jsonify({'error': 'Reset token has expired'}), 400
    
    user.set_password(mongo, data['password'])
    user.clear_reset_token(mongo)
    
    return jsonify({'message': 'Password reset successfully'})

@auth_bp.route('/profile')
@jwt_required()
def get_profile():
    """Get user profile."""
    user_id = get_jwt_identity()
    user = User.get_by_id(mongo, user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': str(user._id),
        'username': user.username,
        'email': user.email,
        'is_verified': user.is_verified,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    })
