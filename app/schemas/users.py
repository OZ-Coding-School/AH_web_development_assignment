from pydantic import BaseModel, EmailStr
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


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
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


class AdminUserRead(UserRead):
    is_active: bool


class AdminUserRoleUpdate(BaseModel):
    user_id: int
    new_role: UserRole


class Message(BaseModel):
    message: str
