from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from backend.extensions import mail

class EmailService:
    @staticmethod
    def send_async_email(app, msg):
        """Send email asynchronously using a background thread"""
        with app.app_context():
            try:
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Failed to send email: {str(e)}")

    @staticmethod
    def send_email(subject, recipients, template=None, **kwargs):
        """
        Send email with optional HTML template
        
        Args:
            subject (str): Email subject
            recipients (list): List of recipient emails
            template (str): Path to template file (relative to templates/email/)
            **kwargs: Template variables
        """
        app = current_app._get_current_object()
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # If template is provided, render HTML body
        if template:
            msg.html = render_template(template, **kwargs)
        
        # Send email in background thread
        thr = Thread(target=EmailService.send_async_email, args=[app, msg])
        thr.start()
        return thr

    @staticmethod
    def send_reset_password_email(user_email, reset_token):
        """Send password reset email"""
        reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={reset_token}"
        EmailService.send_email(
            subject="Password Reset Request",
            recipients=[user_email],
            template="email/reset_password.html",
            reset_url=reset_url
        )

    @staticmethod
    def send_order_confirmation_email(user_email, order):
        """Send order confirmation email"""
        EmailService.send_email(
            subject=f"Order Confirmation - #{order.order_number}",
            recipients=[user_email],
            template="email/order_confirmation.html",
            order=order
        )

    @staticmethod
    def send_account_verification_email(user_email, verification_token):
        """Send account verification email"""
        verify_url = f"{current_app.config['FRONTEND_URL']}/verify-account?token={verification_token}"
        EmailService.send_email(
            subject="Verify Your Account",
            recipients=[user_email],
            template="email/verify_account.html",
            verify_url=verify_url
        )

    @staticmethod
    def send_admin_notification(subject, message):
        """Send notification to admin email"""
        admin_email = current_app.config['ADMIN_EMAIL']
        if admin_email:
            EmailService.send_email(
                subject=subject,
                recipients=[admin_email],
                template="email/admin_notification.html",
                message=message
            )

# Convenience wrapper function for easier import and usage
def send_email(*args, **kwargs):
    return EmailService.send_email(*args, **kwargs)
