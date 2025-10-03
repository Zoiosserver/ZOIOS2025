import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from jinja2 import Template
from typing import List
import logging

logger = logging.getLogger(__name__)

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "noreply@zoios.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "zoios123!@#"),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@zoios.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.zoios.com"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "ZOIOS ERP System"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Initialize FastMail
fastmail = FastMail(conf)

# Email templates
PASSWORD_RESET_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - ZOIOS ERP</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8fafc;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            padding: 30px 40px;
            text-align: center;
        }
        .logo {
            width: 60px;
            height: 60px;
            margin: 0 auto 15px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .header h1 {
            color: white;
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }
        .content {
            padding: 40px;
        }
        .content h2 {
            color: #1f2937;
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 20px;
        }
        .content p {
            margin-bottom: 20px;
            color: #4b5563;
        }
        .reset-button {
            display: inline-block;
            background: #3b82f6;
            color: white;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-weight: 500;
            margin: 20px 0;
            transition: background-color 0.2s;
        }
        .reset-button:hover {
            background: #2563eb;
        }
        .info-box {
            background: #f3f4f6;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .footer {
            background: #f9fafb;
            padding: 30px 40px;
            text-align: center;
            border-top: 1px solid #e5e7eb;
        }
        .footer p {
            margin: 0;
            color: #6b7280;
            font-size: 14px;
        }
        .warning {
            color: #dc2626;
            font-size: 14px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="https://customer-assets.emergentagent.com/job_outreach-pulse-3/artifacts/5adajuhk_Zoios.png" 
                     alt="ZOIOS Logo" style="width: 40px; height: 40px;">
            </div>
            <h1>ZOIOS ERP System</h1>
        </div>
        
        <div class="content">
            <h2>Password Reset Request</h2>
            
            <p>Hello <strong>{{ user_name }}</strong>,</p>
            
            <p>We received a request to reset your password for your ZOIOS ERP account. If you made this request, click the button below to reset your password:</p>
            
            <div style="text-align: center;">
                <a href="{{ reset_link }}" class="reset-button">Reset My Password</a>
            </div>
            
            <div class="info-box">
                <p><strong>Important:</strong></p>
                <ul>
                    <li>This link will expire in <strong>24 hours</strong></li>
                    <li>You can only use this link once</li>
                    <li>If you didn't request this reset, please ignore this email</li>
                </ul>
            </div>
            
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #f3f4f6; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 14px;">{{ reset_link }}</p>
            
            <p class="warning">⚠️ If you did not request a password reset, please contact our support team immediately.</p>
        </div>
        
        <div class="footer">
            <p>© 2025 ZOIOS ERP System. All rights reserved.</p>
            <p>This is an automated email. Please do not reply to this message.</p>
        </div>
    </div>
</body>
</html>
"""

WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to ZOIOS ERP</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8fafc;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .header {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 30px 40px;
            text-align: center;
        }
        .logo {
            width: 60px;
            height: 60px;
            margin: 0 auto 15px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .header h1 {
            color: white;
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }
        .content {
            padding: 40px;
        }
        .content h2 {
            color: #1f2937;
            margin-top: 0;
            margin-bottom: 20px;
            font-size: 20px;
        }
        .content p {
            margin-bottom: 20px;
            color: #4b5563;
        }
        .login-button {
            display: inline-block;
            background: #10b981;
            color: white;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 8px;
            font-weight: 500;
            margin: 20px 0;
        }
        .footer {
            background: #f9fafb;
            padding: 30px 40px;
            text-align: center;
            border-top: 1px solid #e5e7eb;
        }
        .footer p {
            margin: 0;
            color: #6b7280;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <img src="https://customer-assets.emergentagent.com/job_outreach-pulse-3/artifacts/5adajuhk_Zoios.png" 
                     alt="ZOIOS Logo" style="width: 40px; height: 40px;">
            </div>
            <h1>Welcome to ZOIOS ERP</h1>
        </div>
        
        <div class="content">
            <h2>Account Created Successfully!</h2>
            
            <p>Hello <strong>{{ user_name }}</strong>,</p>
            
            <p>Welcome to ZOIOS ERP System! Your account has been created successfully and you're ready to streamline your business operations.</p>
            
            <p><strong>Your Account Details:</strong></p>
            <ul>
                <li><strong>Email:</strong> {{ user_email }}</li>
                <li><strong>Company:</strong> {{ user_company }}</li>
                <li><strong>Account Type:</strong> {{ user_role }}</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="{{ login_url }}" class="login-button">Access Your Dashboard</a>
            </div>
            
            <p>With ZOIOS ERP, you can:</p>
            <ul>
                <li>Manage contacts and business relationships</li>
                <li>Track calls and communications</li>
                <li>Monitor email responses and campaigns</li>
                <li>Analyze business performance with interactive dashboards</li>
                <li>Streamline your business operations</li>
            </ul>
            
            <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
        </div>
        
        <div class="footer">
            <p>© 2025 ZOIOS ERP System. All rights reserved.</p>
            <p>This is an automated email. Please do not reply to this message.</p>
        </div>
    </div>
</body>
</html>
"""

async def send_password_reset_email(email: EmailStr, user_name: str, reset_token: str, base_url: str):
    """Send password reset email with reset link"""
    try:
        reset_link = f"{base_url}/reset-password?token={reset_token}"
        
        template = Template(PASSWORD_RESET_TEMPLATE)
        html_content = template.render(
            user_name=user_name,
            reset_link=reset_link
        )
        
        message = MessageSchema(
            subject="Reset Your ZOIOS ERP Password",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )
        
        await fastmail.send_message(message)
        logger.info(f"Password reset email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False

async def send_welcome_email(email: EmailStr, user_name: str, user_company: str, user_role: str, base_url: str):
    """Send welcome email to new users"""
    try:
        login_url = f"{base_url}/login"
        
        template = Template(WELCOME_EMAIL_TEMPLATE)
        html_content = template.render(
            user_name=user_name,
            user_email=email,
            user_company=user_company,
            user_role=user_role.title(),
            login_url=login_url
        )
        
        message = MessageSchema(
            subject="Welcome to ZOIOS ERP - Account Created Successfully",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )
        
        await fastmail.send_message(message)
        logger.info(f"Welcome email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False

async def send_test_email(email: EmailStr):
    """Send test email to verify SMTP configuration"""
    try:
        html_content = """
        <h2>ZOIOS ERP SMTP Test</h2>
        <p>If you received this email, the SMTP configuration is working correctly.</p>
        <p>© 2025 ZOIOS ERP System</p>
        """
        
        message = MessageSchema(
            subject="ZOIOS ERP - SMTP Test",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )
        
        await fastmail.send_message(message)
        logger.info(f"Test email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send test email to {email}: {str(e)}")
        return False