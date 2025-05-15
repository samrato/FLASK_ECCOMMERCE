from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from backend.services.email import send_email
from backend.models.user import User

class AuthService:
    @staticmethod
    def generate_reset_token(user):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(user.email, salt='password-reset-salt')
    
    @staticmethod
    def verify_reset_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt='password-reset-salt',
                max_age=expiration
            )
        except:
            return None
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def send_reset_email(email, token):
        reset_url = f"https://yourapp.com/reset-password?token={token}"
        send_email(
            subject="Password Reset Request",
            recipients=[email],
            template="email/reset_password.html",
            reset_url=reset_url
        )