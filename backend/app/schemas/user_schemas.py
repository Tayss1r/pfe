from typing import Annotated, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, StringConstraints


class UserCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=100)]
    username: Annotated[str, StringConstraints(max_length=10)]
    fullname: Annotated[str, StringConstraints(min_length=4, max_length=20)]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    fullname: str
    profile_image: str | None = None
    is_verified: bool
    roles: List[str] = []

    class Config:
        from_attributes = True

class SignupResponse(BaseModel):
    message: str

class UserUpdate(BaseModel):
    fullname: Annotated[str, StringConstraints(min_length=4, max_length=20)] | None = None
    username: Annotated[str, StringConstraints(max_length=10)] | None = None
    email: EmailStr | None = None
    phone: str | None = None