import aiosmtplib
from email.message import EmailMessage
from app.config import get_settings

settings = get_settings()


async def send_reset_email(to_email: str, reset_token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "FitTracker - Reset Your Password"
    msg.set_content(
        f"Click the link below to reset your password:\n\n{reset_url}\n\n"
        f"This link expires in 1 hour. If you didn't request this, ignore this email."
    )
    msg.add_alternative(
        f"""<html><body>
        <h2>Reset Your Password</h2>
        <p>Click the button below to reset your FitTracker password:</p>
        <a href="{reset_url}" style="display:inline-block;padding:12px 24px;background:#4F46E5;color:white;text-decoration:none;border-radius:8px;font-weight:bold;">
            Reset Password
        </a>
        <p style="color:#666;margin-top:16px;">This link expires in 1 hour.</p>
        </body></html>""",
        subtype="html",
    )

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
