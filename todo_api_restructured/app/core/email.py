import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, body: str) -> None:
    """Send an HTML email when SMTP is configured."""
    if not settings.email_enabled:
        logger.debug("Email delivery skipped because SMTP is not configured")
        return

    message = MIMEMultipart("alternative")
    message["From"] = settings.FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    smtp = aiosmtplib.SMTP(
        hostname=settings.SMTP_SERVER,
        port=settings.SMTP_PORT,
        use_tls=settings.SMTP_USE_TLS,
        start_tls=settings.SMTP_START_TLS and not settings.SMTP_USE_TLS,
        timeout=30,
    )
    try:
        await smtp.connect()
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
        logger.info("Email sent to %s", to_email)
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
    finally:
        if smtp.is_connected:
            await smtp.quit()


async def notify_task_assigned(user_email: str, task_name: str, admin_email: str) -> None:
    safe_task_name = escape(task_name)
    safe_admin_email = escape(admin_email)
    subject = f"New Task Assigned: {task_name}"
    body = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
      <h2>New Task Assigned</h2>
      <p><b>{safe_admin_email}</b> assigned you a task:</p>
      <p><strong>{safe_task_name}</strong></p><hr><small>{escape(settings.APP_NAME)}</small>
    </body></html>
    """
    await send_email(user_email, subject, body)


async def notify_task_completed(admin_email: str, task_name: str, user_email: str) -> None:
    safe_task_name = escape(task_name)
    safe_user_email = escape(user_email)
    subject = f"Task Completed: {task_name}"
    body = f"""
    <html><body style="font-family: Arial, sans-serif; padding: 20px;">
      <h2>Task Completed</h2>
      <p>User <b>{safe_user_email}</b> completed:</p>
      <p><strong>{safe_task_name}</strong></p><hr><small>{escape(settings.APP_NAME)}</small>
    </body></html>
    """
    await send_email(admin_email, subject, body)
