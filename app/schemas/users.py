import re

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.core.enums import UserRole, Gender, Department


class UserBase(BaseModel):
    email: EmailStr
    name: str
    department: Department
    gender: Gender
    phone_number: str


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_format(cls, v: str) -> str:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
        if not re.match(pattern, v):
            raise ValueError("비밀번호는 대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다.")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(UserBase):
    id: int
    role: UserRole

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    department: Optional[Department] = None
    phone_number: Optional[str] = None


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password_format(cls, v: str) -> str:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
        if not re.match(pattern, v):
            raise ValueError("비밀번호는 대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다.")
        return v


class AdminUserRead(UserRead):
    is_active: bool


class AdminUserRoleUpdate(BaseModel):
    user_id: int
    new_role: UserRole


class Message(BaseModel):
    message: str
