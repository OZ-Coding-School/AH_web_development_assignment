from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.medical_records import MedicalRecord, XrayImage


class MedicalRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, medical_record: MedicalRecord, xray_image: XrayImage) -> MedicalRecord:
        self.db.add(medical_record)
        await self.db.flush()  # ID 생성을 위해 flush

        xray_image.record_id = medical_record.id
        self.db.add(xray_image)

        await self.db.commit()
        await self.db.refresh(medical_record, ["xray_images"])
        return medical_record

    async def get_by_id(self, record_id: int) -> Optional[MedicalRecord]:
        result = await self.db.execute(
            select(MedicalRecord).where(MedicalRecord.id == record_id).options(selectinload(MedicalRecord.xray_images))
        )
        return result.scalars().first()

    async def get_by_patient_id(self, patient_id: int) -> Sequence[MedicalRecord]:
        result = await self.db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(MedicalRecord.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_chart_number(self, chart_number: str) -> Optional[MedicalRecord]:
        result = await self.db.execute(select(MedicalRecord).where(MedicalRecord.chart_number == chart_number))
        return result.scalars().first()
