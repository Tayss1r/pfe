import logging
import uuid
from typing import Any
from itsdangerous import URLSafeTimedSerializer

import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


from datetime import timedelta, datetime

from app.core.config import settings
from app.celery_tasks import send_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

serializer = URLSafeTimedSerializer(
        secret_key=settings.JWT_SECRET,
        salt="email-configuration"
    )

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False):
    payload = {"user": user_data, "exp": datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY)
    ), "jti": str(uuid.uuid4()), "refresh": refresh}

    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return token

def decode_token(token: str) -> Any | None:
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )

        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None

def create_url_safe_token(data: dict):
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str, max_age: int = 84600):
    return serializer.loads(token, max_age=max_age)

def send_verification_email(user):
    email = user.email
    token = create_url_safe_token({"email": email})

    link = f"http://{settings.DOMAIN}/api/v1/auth/verify/{token}"
    html = f"""
            <!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="UTF-8">
                <title>Verify Your Email</title>
                </head>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
                <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; margin-top: 40px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <tr>
                    <td style="padding: 40px; text-align: center;">
                        <h2 style="color: #333333;">Welcome to Cabinet Medical!</h2>
                        <p style="color: #555555; font-size: 16px; line-height: 1.5;">
                        Thank you for registering. Please verify your email address to get started.
                        </p>
                        <a href="{link}" 
                        style="display: inline-block; margin-top: 25px; padding: 12px 25px; background-color: #4CAF50; color: #ffffff; text-decoration: none; font-weight: bold; border-radius: 5px; transition: background 0.3s;">
                        Verify Email
                        </a>
                        <p style="margin-top: 30px; color: #888888; font-size: 14px;">
                        If you didn’t create an account, you can safely ignore this email.
                        </p>
                    </td>
                    </tr>
                </table>
                </body>
                </html>
            """
    emails = [email]
    subject = "Verify your Email"
    send_email.delay(emails, subject, html)

def send_verification_code_email(user, code: str):
    """Send 6-digit verification code via email"""
    email = user.email
    html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <title>Email Verification Code</title>
            </head>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
            <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; margin-top: 40px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <tr>
                <td style="padding: 40px; text-align: center;">
                    <h2 style="color: #333333;">Welcome to Cabinet Medical!</h2>
                    <p style="color: #555555; font-size: 16px; line-height: 1.5;">
                    Thank you for registering. Use the following code to verify your email address:
                    </p>
                    <div style="margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #4CAF50;">{code}</span>
                    </div>
                    <p style="color: #888888; font-size: 14px;">
                    This code will expire in 10 minutes.
                    </p>
                    <p style="margin-top: 30px; color: #888888; font-size: 14px;">
                    If you didn't create an account, you can safely ignore this email.
                    </p>
                </td>
                </tr>
            </table>
            </body>
            </html>
            """
    emails = [email]
    subject = "Your Email Verification Code"
    send_email.delay(emails, subject, html)