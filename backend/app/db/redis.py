from redis.asyncio import Redis
from ..core.config import settings

JTI_EXPIRY = 3600
RESET_CODE_EXPIRY = 600  # 10 minutes
EMAIL_VERIFICATION_CODE_EXPIRY = 600  # 10 minutes

token_blocklist = Redis.from_url(settings.REDIS_URL)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    value = await token_blocklist.get(jti)
    return value is not None


# Password reset code functions
async def store_reset_code(email: str, hashed_code: str) -> None:
    """Store hashed reset code with expiry"""
    key = f"reset_code:{email.lower()}"
    await token_blocklist.set(name=key, value=hashed_code, ex=RESET_CODE_EXPIRY)

async def get_reset_code(email: str) -> str | None:
    """Get stored hashed reset code"""
    key = f"reset_code:{email.lower()}"
    value = await token_blocklist.get(key)
    return value.decode() if value else None

async def delete_reset_code(email: str) -> None:
    """Delete reset code after successful use"""
    key = f"reset_code:{email.lower()}"
    await token_blocklist.delete(key)


# Email verification code functions
async def store_email_verification_code(email: str, hashed_code: str) -> None:
    """Store hashed email verification code with expiry"""
    key = f"email_verification_code:{email.lower()}"
    await token_blocklist.set(name=key, value=hashed_code, ex=EMAIL_VERIFICATION_CODE_EXPIRY)

async def get_email_verification_code(email: str) -> str | None:
    """Get stored hashed email verification code"""
    key = f"email_verification_code:{email.lower()}"
    value = await token_blocklist.get(key)
    return value.decode() if value else None

async def delete_email_verification_code(email: str) -> None:
    """Delete email verification code after successful use"""
    key = f"email_verification_code:{email.lower()}"
    await token_blocklist.delete(key)