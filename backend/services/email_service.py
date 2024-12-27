from flask import current_app, render_template_string
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import threading

mail = Mail()

def init_email(app):
    """Initialize email service."""
    app.config.update(
        MAIL_SERVER=app.config.get('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=app.config.get('MAIL_PORT', 587),
        MAIL_USE_TLS=app.config.get('MAIL_USE_TLS', True),
        MAIL_USERNAME=app.config.get('MAIL_USERNAME'),
        MAIL_PASSWORD=app.config.get('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=app.config.get('MAIL_DEFAULT_SENDER')
    )
    mail.init_app(app)

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipient, template, **kwargs):
    """Send email using template."""
    msg = Message(
        subject,
        recipients=[recipient],
        html=render_template_string(template, **kwargs)
    )
    
    # Send email asynchronously
    threading.Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()

def generate_token(email):
    """Generate verification token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def verify_token(token, expiration=3600):
    """Verify token."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except:
        return None

# Email Templates
VERIFY_EMAIL_TEMPLATE = """
<p>Welcome to Skript'd!</p>
<p>Please click the link below to verify your email address:</p>
<p><a href="{{ verify_url }}">{{ verify_url }}</a></p>
<p>This link will expire in 1 hour.</p>
<p>If you did not create an account, please ignore this email.</p>
"""

RESET_PASSWORD_TEMPLATE = """
<p>Hello,</p>
<p>You have requested to reset your password. Please click the link below:</p>
<p><a href="{{ reset_url }}">{{ reset_url }}</a></p>
<p>This link will expire in 1 hour.</p>
<p>If you did not request a password reset, please ignore this email.</p>
"""

def send_verification_email(email, verification_url):
    """Send verification email."""
    send_email(
        'Verify your Skript\'d account',
        email,
        VERIFY_EMAIL_TEMPLATE,
        verify_url=verification_url
    )

def send_password_reset_email(email, reset_url):
    """Send password reset email."""
    send_email(
        'Reset your Skript\'d password',
        email,
        RESET_PASSWORD_TEMPLATE,
        reset_url=reset_url
    )
