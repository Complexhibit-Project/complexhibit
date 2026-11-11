"""
Email service for sending notifications using Direct SMTP SSL (Port 465).
"""

import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

# Frontend base URL for email links (from environment)
FRONTEND_URL = settings.FRONTEND_URL

def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: Optional[str] = None
) -> bool:
    """
    Send an email using Direct SMTP SSL (Port 465).
    Validated as working in the UMA environment.
    """
    if not settings.SMTP_HOST:
        print(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
        return True
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        
        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))
        
        # Consistent credential cleaning
        smtp_password = settings.SMTP_PASSWORD.replace(" ", "").strip() if settings.SMTP_PASSWORD else ""
        smtp_user = settings.SMTP_USER.strip() if settings.SMTP_USER else ""
        
        print(f"[EMAIL] Connecting directly to Gmail (SSL 465) for {to_email}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(smtp_user, smtp_password)
            server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
        
        print(f"[EMAIL SUCCESS] Sent to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed: {e}")
        return False

def send_registration_confirmation(user_email: str, user_name: str) -> bool:
    user_name = html.escape(user_name or "")
    subject = "[Complexhibit] Thank you for registering!"
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4F46E5;">Welcome to Complexhibit!</h2>
            <p>Dear {user_name},</p>
            <p>Thank you for registering on <strong>Complexhibit</strong>. Your request is pending approval.</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{FRONTEND_URL}" 
                   style="display: inline-block; padding: 12px 24px; background: linear-gradient(to right, #4F46E5, #7C3AED); 
                          color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Visit Complexhibit
                </a>
            </p>
            <p>Best regards,<br><strong>The Complexhibit Team</strong></p>
        </div>
    </body>
    </html>
    """
    return send_email(user_email, subject, body_html)

def send_password_reset_email(user_email: str, user_name: str, reset_url: str) -> bool:
    user_name = html.escape(user_name or "")
    subject = "[Complexhibit] Reset your password"
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4F46E5;">Reset your password</h2>
            <p>Dear {user_name},</p>
            <p>We received a request to reset the password for your <strong>Complexhibit</strong> account.
               Click the button below to choose a new password. This link will expire in 60 minutes.</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}"
                   style="display: inline-block; padding: 12px 24px; background: linear-gradient(to right, #4F46E5, #7C3AED);
                          color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Reset Password
                </a>
            </p>
            <p>If you did not request a password reset, you can safely ignore this email.</p>
            <p>Best regards,<br><strong>The Complexhibit Team</strong></p>
        </div>
    </body>
    </html>
    """
    return send_email(user_email, subject, body_html)

def send_admin_notification(user_email: str, user_name: str, user_type: str = None, institution_type: str = None) -> bool:
    user_name = html.escape(user_name or "")
    user_email = html.escape(user_email or "")
    user_type = html.escape(user_type) if user_type else user_type
    institution_type = html.escape(institution_type) if institution_type else institution_type
    subject = f"[Complexhibit] New user registration: {user_email}"
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4F46E5;">New User Registration</h2>
            <table style="margin: 20px 0; border-collapse: collapse; width: 100%;">
                <tr><td style="padding: 10px; background: #F3F4F6; font-weight: bold; width: 40%; border: 1px solid #E5E7EB;">Name:</td><td style="padding: 10px; border: 1px solid #E5E7EB;">{user_name}</td></tr>
                <tr><td style="padding: 10px; background: #F3F4F6; font-weight: bold; border: 1px solid #E5E7EB;">Email:</td><td style="padding: 10px; border: 1px solid #E5E7EB;">{user_email}</td></tr>
                <tr><td style="padding: 10px; background: #F3F4F6; font-weight: bold; border: 1px solid #E5E7EB;">User Type:</td><td style="padding: 10px; border: 1px solid #E5E7EB;">{user_type.capitalize() if user_type else 'Individual'}</td></tr>
                {f'<tr><td style="padding: 10px; background: #F3F4F6; font-weight: bold; border: 1px solid #E5E7EB;">Institution Type:</td><td style="padding: 10px; border: 1px solid #E5E7EB;">{institution_type}</td></tr>' if institution_type else ''}
            </table>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{FRONTEND_URL}/admin/users" 
                   style="display: inline-block; padding: 14px 28px; background: #4F46E5; color: white; border-radius: 8px; font-weight: bold;">
                    Go to Admin Panel
                </a>
            </p>
        </div>
    </body>
    </html>
    """
    return send_email(settings.ADMIN_EMAIL, subject, body_html)

def send_approval_notification(user_email: str, approved: bool) -> bool:
    if approved:
        subject = "[Complexhibit] Your account has been approved!"
        heading = "Your account is ready!"
        msg = "Great news! Your <strong>Complexhibit</strong> account has been approved. You can now log in and start exploring."
        button_label = "Log in to Complexhibit"
        button_url = f"{FRONTEND_URL}/auth/login"
    else:
        subject = "[Complexhibit] Registration Update"
        heading = "Registration update"
        msg = "We regret to inform you that your registration request has not been approved at this time. If you think this is a mistake, please contact our team."
        button_label = "Visit Complexhibit"
        button_url = FRONTEND_URL

    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #4F46E5;">{heading}</h2>
            <p>{msg}</p>
            <p style="text-align: center; margin: 30px 0;">
                <a href="{button_url}"
                   style="display: inline-block; padding: 12px 24px; background: linear-gradient(to right, #4F46E5, #7C3AED);
                          color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    {button_label}
                </a>
            </p>
            <p>Best regards,<br><strong>The Complexhibit Team</strong></p>
        </div>
    </body>
    </html>
    """
    return send_email(user_email, subject, body_html)
