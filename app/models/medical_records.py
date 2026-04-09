from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin


if TYPE_CHECKING:
    from app.models.patients import Patient
    from app.models.users import User


class MedicalRecord(Base, TimestampMixin):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    patient_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("patients.id", ondelete="RESTRICT"), index=True)
    chart_number: Mapped[str] = mapped_column(String(50), unique=True)
    symptoms: Mapped[str] = mapped_column(Text)

    # patient 객체 참조 관계 설정
    patient: Mapped["Patient"] = relationship(back_populates="medical_records")
    # xray_image 객체 역참조관계 설정
    xray_images: Mapped[list["XrayImage"]] = relationship(back_populates="medical_record", passive_deletes=True)


class XrayImage(Base, TimestampMixin):
    __tablename__ = "xray_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    record_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("medical_records.id", ondelete="CASCADE"), index=True)
    uploader_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    image_url: Mapped[str] = mapped_column(String(2048))

    # medical_record 객체 참조 관계 설정
    medical_record: Mapped["MedicalRecord"] = relationship(back_populates="xray_images")
    # uploader 객체 참조 관계 설정
    uploader: Mapped["User"] = relationship(back_populates="uploaded_xray_images")
