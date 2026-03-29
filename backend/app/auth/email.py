import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_reset_email(to_email: str, reset_token: str) -> bool:
    """Send password reset email with reset link."""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = "FitTracker - Reset Your Password"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; text-align: center;">FitTracker</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333;">Password Reset Request</h2>
            <p style="color: #666;">You requested to reset your password. Click the button below to set a new password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}"
                   style="background: #667eea; color: white; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold;">
                    Reset Password
                </a>
            </div>
            <p style="color: #999; font-size: 14px;">This link expires in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
            <p style="color: #999; font-size: 14px;">If you didn't request this, please ignore this email.</p>
        </div>
    </body>
    </html>
    """

    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
        )
        logger.info(f"Reset email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send reset email to {to_email}: {e}")
        return False
