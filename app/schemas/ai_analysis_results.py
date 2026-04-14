from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional


class AIAnalysisBase(BaseModel):
    record_id: int
    is_pneumonia: bool
    confidence: Decimal = Field(..., ge=0, le=100)
    heatmap_url: Optional[str] = None
    ai_model: str = Field(..., max_length=50)


class AIAnalysisCreate(AIAnalysisBase):
    pass


class AIAnalysisRead(AIAnalysisBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
