import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


async def send_email(to_email: str, subject: str, body: str):
    try:
        message = MIMEMultipart("alternative")
        message["From"] = settings.FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        smtp = aiosmtplib.SMTP(
            hostname="smtp.gmail.com",
            port=465,
            use_tls=True,      #  TLS FROM START
            timeout=30,
        )

        await smtp.connect()
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        await smtp.send_message(message)
        await smtp.quit()

        print(f"✅ Email sent to {to_email}")

    except Exception as e:
        print("❌ EMAIL ERROR TYPE:", type(e))
        print("❌ EMAIL ERROR:", e)


async def notify_task_assigned(user_email: str, task_name: str, admin_email: str):
    subject = f"New Task Assigned: {task_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>New Task Assigned</h2>
        <p>Hi,</p>
        <p><b>{admin_email}</b> assigned you a task:</p>
        <p><strong>{task_name}</strong></p>
        <hr>
        <small>{settings.APP_NAME}</small>
    </body>
    </html>
    """
    await send_email(user_email, subject, body)


async def notify_task_completed(admin_email: str, task_name: str, user_email: str):
    subject = f"Task Completed: {task_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Task Completed</h2>
        <p>User <b>{user_email}</b> completed:</p>
        <p><strong>{task_name}</strong></p>
        <hr>
        <small>{settings.APP_NAME}</small>
    </body>
    </html>
    """
    await send_email(admin_email, subject, body)
