from typing import List, Optional
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import aiosmtplib

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from .core.config import settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

mail_config = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

mail = FastMail(mail_config)


def create_message(recipients: List[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype=MessageType.html
    )
    return message


async def send_email_with_attachments(
    recipients: List[str],
    subject: str,
    body: str,
    attachments: Optional[List[dict]] = None,
) -> bool:
    """
    Send an email with attachments using direct SMTP.
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        body: HTML body content
        attachments: List of dicts with 'file' (bytes), 'filename', 'content_type'
    
    Returns:
        True if email was sent successfully
    """
    # Create multipart message
    msg = MIMEMultipart()
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    
    # Attach HTML body
    msg.attach(MIMEText(body, "html"))
    
    # Attach files
    if attachments:
        for attachment in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment["file"])
            encoders.encode_base64(part)
            
            filename = attachment.get("filename", "attachment")
            content_type = attachment.get("content_type", "application/octet-stream")
            
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={filename}",
            )
            part.add_header("Content-Type", content_type)
            msg.attach(part)
    
    # Send via SMTP
    await aiosmtplib.send(
        msg,
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        start_tls=settings.MAIL_STARTTLS,
    )
    
    return True


def create_message_with_attachments(
    recipients: List[str],
    subject: str,
    body: str,
    attachments: Optional[List[dict]] = None
):
    """Create a message schema - kept for compatibility."""
    return MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype=MessageType.html,
    )