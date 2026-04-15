from fastapi import UploadFile, File
from pydantic import BaseModel, Field, field_validator
import re
from datetime import datetime
from typing import Optional


class MedicalRecordBase(BaseModel):
    patient_id: int = Field(..., examples=[1], ge=1)
    chart_number: str = Field(..., examples=["20260101-0004"])
    symptoms: str = Field(..., examples=["발열, 황록색 객담, 기침, 콧물"])


class MedicalRecordCreate(MedicalRecordBase):
    xray_image: UploadFile = File(...)

    @field_validator("chart_number")
    @classmethod
    def validate_chart_number(cls, v: str) -> str:
        pattern = r"^\d{8}-\d{4}$"
        if not re.match(pattern, v):
            raise ValueError("올바르지 않은 차트 번호 형식입니다. (예: 20260101-9231)")
        return v


class MedicalRecordListRead(BaseModel):
    id: int
    chart_number: str
    symptoms: str
    created_at: datetime

    @field_validator("symptoms")
    @classmethod
    def truncate_symptoms(cls, v: str) -> str:
        if len(v) > 100:
            return v[:100] + "..."
        return v

    class Config:
        from_attributes = True


class MedicalRecordRead(MedicalRecordBase):
    id: int
    xray_image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
