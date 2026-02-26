from datetime import timedelta, datetime
import random
from fastapi import APIRouter, Depends, status
from itsdangerous import SignatureExpired, BadSignature
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse, RedirectResponse

from ..db.database import get_session
from ..db.redis import store_email_verification_code, get_email_verification_code, \
    delete_email_verification_code, add_jti_to_blocklist, store_reset_code, get_reset_code, delete_reset_code
from ..errors import RegistrationFailed, AccountNotVerified, InvalidCredentials, InvalidVerificationCode, \
    UserNotFound, InvalidToken, InvalidResetCode, PasswordsDoNotMatch
from ..schemas.email_schemas import Email, ResendEmailVerificationCodeModel, EmailVerificationCodeVerifyModel, \
    PasswordResetRequestModel, PasswordResetCodeVerifyModel, PasswordResetCodeConfirmModel
from ..schemas.user_schemas import UserCreate, UserLogin, SignupResponse, UserOut
from ..services.user_service import UserService
from ..utils import send_verification_code_email, verify, create_access_token, decode_url_safe_token, \
    create_url_safe_token, hash
from ..dependencies import AccessTokenBearer, get_current_user, RefreshTokenBearer
from ..celery_tasks import send_email

REFRESH_TOKEN_EXPIRY = 2
auth_router = APIRouter()

@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, session: AsyncSession = Depends(get_session)):
    email = user.email
    user_exists = await UserService.user_exists(email, session)
    if user_exists:
        raise RegistrationFailed()
    new_user = await UserService.create_user(user, session)

    # Generate 6-digit verification code
    code = str(random.randint(100000, 999999))
    hashed_code = hash(code)

    # Store hashed code in Redis with expiry
    await store_email_verification_code(email, hashed_code)

    # Send verification code via email
    send_verification_code_email(new_user, code)

    return {
        "message": "Account created! A 6-digit verification code has been sent to your email.",
        "email": email
    }


@auth_router.post("/login")
async def login(login_data: UserLogin, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await UserService.get_user_by_email(email, session)

    if user and verify(password, user.password):
        if not user.is_verified:
            raise AccountNotVerified()
        access_token = create_access_token(
            user_data={
                "email": user.email,
                "user_uid": str(user.id),
                "role": user.role,
            }
        )
        refresh_token = create_access_token(
            user_data={"email": user.email, "user_uid": str(user.id)},
            refresh=True,
            expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
        )

        response = JSONResponse(
            content={
                "message": "Login successful",
                "access_token": access_token,
                "user": {"email": user.email, "uid": str(user.id), "role": user.role},
            }
        )

        # Clear any existing refresh_token cookie first
        response.delete_cookie(
            key="refresh_token",
            path="/",
            samesite="lax"
        )

        # Store the NEW refresh token in an HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=REFRESH_TOKEN_EXPIRY * 24 * 3600,
            path="/",
            httponly=True,  # protect against XSS
            secure=False,
            samesite="lax",  # Changed from "none" to "lax" for localhost
        )
        return response

    raise InvalidCredentials()


@auth_router.get('/verify/{token}', response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    try:
        token_data = decode_url_safe_token(token, max_age=60)
        user_email = token_data.get("email")
        if not user_email:
            return JSONResponse(
                {"message": "Invalid token data."},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Fetch user
        user = await UserService.get_user_by_email(user_email, session)
        if not user:
            return JSONResponse(
                {"message": "User not found."},
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Already verified
        if user.is_verified:
            return RedirectResponse(url="http://localhost:4200/login?verify=already")

        # Update verification
        await UserService.update_user(user, {"is_verified": True}, session)
        return RedirectResponse(url="http://localhost:4200/login?verify=success")

    except SignatureExpired:
        return RedirectResponse(url="http://localhost:4200/login?verify=expired")
    except BadSignature:
        return JSONResponse(
            {"message": "Invalid verification link."},
            status_code=status.HTTP_400_BAD_REQUEST
        )


@auth_router.post('/resend-verification-email')
async def resend_verif_email(request: Email, session: AsyncSession = Depends(get_session)):
    user = await UserService.get_user_by_email(request.email, session)
    if user is not None and not user.is_verified:
        # Generate 6-digit verification code
        code = str(random.randint(100000, 999999))
        hashed_code = hash(code)

        # Store hashed code in Redis with expiry
        await store_email_verification_code(request.email, hashed_code)

        # Send verification code via email
        send_verification_code_email(user, code)
    # returned a generic message fo r securty purposes
    return JSONResponse(
        {"message": "If the email is registered, a verification link will be sent"},
        status_code=status.HTTP_200_OK
    )


@auth_router.post('/send-verification-code')
async def send_verification_code(request: ResendEmailVerificationCodeModel,
                                 session: AsyncSession = Depends(get_session)):
    """Send a 6-digit verification code to the user's email"""
    user = await UserService.get_user_by_email(request.email, session)
    if user is not None and not user.is_verified:
        # Generate 6-digit verification code
        code = str(random.randint(100000, 999999))
        hashed_code = hash(code)

        # Store hashed code in Redis with expiry
        await store_email_verification_code(request.email, hashed_code)

        # Send verification code via email
        send_verification_code_email(user, code)

    # Return generic message for security purposes
    return JSONResponse(
        {"message": "If the email is registered and not verified, a verification code will be sent"},
        status_code=status.HTTP_200_OK
    )


@auth_router.post('/verify-email-code')
async def verify_email_with_code(data: EmailVerificationCodeVerifyModel, session: AsyncSession = Depends(get_session)):
    """Verify email using 6-digit code"""
    email = data.email
    code = data.code

    # Get stored hashed code
    stored_hashed_code = await get_email_verification_code(email)
    if not stored_hashed_code:
        raise InvalidVerificationCode()

    # Verify code
    if not verify(code, stored_hashed_code):
        raise InvalidVerificationCode()

    # Get user
    user = await UserService.get_user_by_email(email, session)
    if not user:
        raise UserNotFound()

    # Already verified
    if user.is_verified:
        return JSONResponse(
            {"message": "Email already verified"},
            status_code=status.HTTP_200_OK
        )

    # Update verification status
    await UserService.update_user(user, {"is_verified": True}, session)

    # Invalidate code (single-use)
    await delete_email_verification_code(email)

    return JSONResponse(
        {"message": "Email verified successfully"},
        status_code=status.HTTP_200_OK
    )


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer)):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidToken()


@auth_router.get('/logout')
async def revoke_token(token_data=Depends(AccessTokenBearer())):
    jti = token_data['jti']
    await add_jti_to_blocklist(jti)
    response = JSONResponse(
        content={
            "message": "Logged out Succesufully"
        }, status_code=status.HTTP_200_OK
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return response


@auth_router.post('/reset_password')
async def reset_pasword(email_data: PasswordResetRequestModel):
    email = email_data.email
    client = email_data.client or "web"

    if client == "mobile":
        # Generate 6-digit code for mobile
        code = str(random.randint(100000, 999999))
        hashed_code = hash(code)

        # Store hashed code in Redis with expiry
        await store_reset_code(email, hashed_code)

        # Send code via email
        html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <title>Password Reset Code</title>
            </head>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
            <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; margin-top: 40px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <tr>
                <td style="padding: 40px; text-align: center;">
                    <h2 style="color: #333333;">Password Reset Code</h2>
                    <p style="color: #555555; font-size: 16px; line-height: 1.5;">
                    Use the following code to reset your password:
                    </p>
                    <div style="margin: 30px 0; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #4CAF50;">{code}</span>
                    </div>
                    <p style="color: #888888; font-size: 14px;">
                    This code will expire in 10 minutes.
                    </p>
                    <p style="margin-top: 30px; color: #888888; font-size: 14px;">
                    If you didn't request a password reset, you can safely ignore this email.
                    </p>
                </td>
                </tr>
            </table>
            </body>
            </html>
            """
        emails = [email]
        subject = "Your Password Reset Code"
        send_email.delay(emails, subject, html)

        return JSONResponse(content={
            "message": "A 6-digit reset code has been sent to your email"
        }, status_code=status.HTTP_200_OK)

    # Existing web flow with link
    token = create_url_safe_token({"email": email})

    link = f"http://localhost:4200//reset-password/{token}"
    html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <meta charset="UTF-8">
            <title>Reset Your Password</title>
            </head>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
            <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; background-color: #ffffff; margin-top: 40px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <tr>
                <td style="padding: 40px; text-align: center;">
                    <h2 style="color: #333333;">Reset Your Password</h2>
                    <p style="color: #555555; font-size: 16px; line-height: 1.5;">
                    We received a request to reset your password. Click the button below to choose a new password.
                    </p>
                    <a href="{link}" 
                    style="display: inline-block; margin-top: 25px; padding: 12px 25px; background-color: #4CAF50; color: #ffffff; text-decoration: none; font-weight: bold; border-radius: 5px; transition: background 0.3s;">
                    Reset Password
                    </a>
                    <p style="margin-top: 30px; color: #888888; font-size: 14px;">
                    If you didn’t request a password reset, you can safely ignore this email.
                    </p>
                </td>
                </tr>
            </table>
            </body>
            </html>
            """
    emails = [email]
    subject = "Reset you password"
    send_email.delay(emails, subject, html)

    return JSONResponse(content={
        "message": "Please check your email inbox to reset you password"
    }, status_code=status.HTTP_200_OK)


@auth_router.post('/verify_reset_code')
async def verify_reset_code(data: PasswordResetCodeVerifyModel):
    """Verify 6-digit reset code without resetting password (for mobile clients)"""
    email = data.email
    code = data.code

    # Get stored hashed code
    stored_hashed_code = await get_reset_code(email)
    if not stored_hashed_code:
        raise InvalidResetCode()

    # Verify code
    if not verify(code, stored_hashed_code):
        raise InvalidResetCode()

    return JSONResponse(content={
        "message": "Code verified successfully"
    }, status_code=status.HTTP_200_OK)


@auth_router.post('/reset_password_code')
async def reset_password_with_code(
        data: PasswordResetCodeConfirmModel,
        session: AsyncSession = Depends(get_session)
):
    """Reset password using 6-digit code (for mobile clients)"""
    email = data.email
    code = data.code
    new_password = data.new_password

    # Get stored hashed code
    stored_hashed_code = await get_reset_code(email)
    if not stored_hashed_code:
        raise InvalidResetCode()

    # Verify code
    if not verify(code, stored_hashed_code):
        raise InvalidResetCode()

    # Get user
    user = await UserService.get_user_by_email(email, session)
    if not user:
        raise UserNotFound()

    # Update password
    await UserService.update_user(user, {'password': hash(new_password)}, session)

    # Invalidate code (single-use)
    await delete_reset_code(email)

    return JSONResponse(content={
        "message": "Password has been updated successfully"
    }, status_code=status.HTTP_200_OK)


@auth_router.post('/reset_password_confirm/{token}')
async def reset_account_pasword(token: str, passwords: PasswordResetCodeConfirmModel,
                                session: AsyncSession = Depends(get_session)):
    if passwords.new_password != passwords.confirm_new_password:
        raise PasswordsDoNotMatch()
    token_data = decode_url_safe_token(token)

    user_email = token_data.get('email')
    if user_email:
        user = await UserService.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        await UserService.update_user(user, {'password': hash(passwords.new_password)}, session)
        return JSONResponse(content={
            "message": "Password has been updated successfully"
        }, status_code=status.HTTP_200_OK)
    return JSONResponse(content={
        "message": "Error occured during password reset"
    }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.get('/me', response_model=UserOut)
async def get_curr_user(user=Depends(get_current_user)):
    return user
