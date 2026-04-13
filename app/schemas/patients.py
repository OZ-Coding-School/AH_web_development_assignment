from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.core.enums import Gender


class PatientBase(BaseModel):
    name: str = Field(..., examples=["홍길동"])
    age: int = Field(..., examples=[45])
    gender: Gender = Field(..., examples=[Gender.M, Gender.F])
    phone_number: str = Field(..., examples=["01012345678"])


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    name: Optional[str] = Field(None, examples=["홍길순"])
    phone_number: Optional[str] = Field(None, examples=["01098765432"])


class PatientRead(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientMessage(BaseModel):
    message: str
