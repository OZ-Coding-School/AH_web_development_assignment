from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Boolean, Numeric, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin


if TYPE_CHECKING:
    from app.models.medical_records import MedicalRecord


class AIAnalysis(Base, TimestampMixin):
    __tablename__ = "ai_analysis_results"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("medical_records.id", ondelete="CASCADE"), index=True)
    is_pneumonia: Mapped[bool] = mapped_column(Boolean)
    # confidence 입력 시 DB레벨에서 유효성 검증을 하도록 CheckConstraint 사용
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), CheckConstraint("confidence >= 0 AND confidence <= 100"))
    heatmap_url: Mapped[str] = mapped_column(String(2048))
    ai_model: Mapped[str] = mapped_column(String(50))
    # medical_record 객체에 대해서 참조 관계 설정
    medical_record: Mapped["MedicalRecord"] = relationship(back_populates="ai_analyses")
