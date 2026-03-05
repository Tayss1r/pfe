from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

from .services.user_service import UserService
from .utils import decode_token
from .db.database import get_session
from .db.redis import token_in_blocklist
from .errors import *
from sqlalchemy.ext.asyncio import AsyncSession


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error = auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials # scheme, (credentials)
        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()
        if await token_in_blocklist(token_data['jti']):
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child class")

class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        token = credentials.credentials
        payload = decode_token(token)

        if payload.get("refresh"):
            raise AccessTokenRequired()

        return payload

async def RefreshTokenBearer(request: Request) -> dict:
    """Read refresh token from HttpOnly cookie."""
    token = request.cookies.get("refresh_token")
    if not token:
        raise RefreshTokenRequired()

    payload = decode_token(token)

    if not payload.get("refresh"):
        raise RefreshTokenRequired()

    return payload

async def get_current_user(token_data=Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):
    email = token_data['user']['email']
    user = await UserService.get_user_by_email(email, session)
    return user


class RoleChecker:
    """Dependency to check if user has required role(s)"""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        token_data: dict = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session),
    ) -> bool:
        user = await UserService.get_user_by_email(
            token_data["user"]["email"], session
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Check if user has any of the allowed roles
        user_roles = [role.name.lower() for role in user.roles]
        for role in self.allowed_roles:
            if role.lower() in user_roles:
                return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )