import resend
from app.config import get_settings

settings = get_settings()
resend.api_key = settings.RESEND_API_KEY


def send_reset_email(to_email: str, reset_token: str):
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": [to_email],
        "subject": "FitTracker - Reset Your Password",
        "html": f"""<html><body>
        <h2>Reset Your Password</h2>
        <p>Click the button below to reset your FitTracker password:</p>
        <a href="{reset_url}" style="display:inline-block;padding:12px 24px;background:#22c55e;color:white;text-decoration:none;border-radius:8px;font-weight:bold;">
            Reset Password
        </a>
        <p style="color:#666;margin-top:16px;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
        </body></html>""",
    })
