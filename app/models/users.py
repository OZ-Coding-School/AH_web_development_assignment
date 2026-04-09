from typing import TYPE_CHECKING

from sqlalchemy import String, Enum, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.databases import Base
from app.core.db.models import TimestampMixin
from app.core.enums import UserRole, Gender


if TYPE_CHECKING:
    from app.models.medical_records import XrayImage


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    nickname: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    phone_number: Mapped[str] = mapped_column(String(11))
    gender: Mapped[str] = mapped_column(Enum(Gender))
    is_active: Mapped[bool] = mapped_column(default=True)
    # 업로드 한 xray 이미지 객체 역참조 관계 설정
    uploaded_xray_images: Mapped[list["XrayImage"]] = relationship(back_populates="uploader", passive_deletes=True)
