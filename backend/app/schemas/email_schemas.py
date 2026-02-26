from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr

class EmailModel(BaseModel):
    addresses: List[str]

class PasswordResetRequestModel(BaseModel):
    email: str
    client: Optional[Literal["web", "mobile"]] = "web"

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str

class PasswordResetCodeConfirmModel(BaseModel):
    email: str
    code: str
    new_password: str

class PasswordResetCodeVerifyModel(BaseModel):
    email: str
    code: str

class Email(BaseModel):
    email: EmailStr

# Email verification with 6-digit code
class EmailVerificationCodeVerifyModel(BaseModel):
    email: str
    code: str

class ResendEmailVerificationCodeModel(BaseModel):
    email: str