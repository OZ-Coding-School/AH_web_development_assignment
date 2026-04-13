from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.patients import Patient
from app.core.enums import Gender


class PatientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, patient: Patient) -> Patient:
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def get_by_id(self, patient_id: int) -> Optional[Patient]:
        result = await self.db.execute(select(Patient).where(Patient.id == patient_id))
        return result.scalars().first()

    async def get_patients(
        self,
        name: Optional[str] = None,
        gender: Optional[Gender] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
    ) -> Sequence[Patient]:
        stmt = select(Patient)
        filters = []
        if name:
            filters.append(Patient.name.contains(name))
        if gender:
            filters.append(Patient.gender == gender)
        if min_age is not None:
            filters.append(Patient.age >= min_age)
        if max_age is not None:
            filters.append(Patient.age <= max_age)

        if filters:
            stmt = stmt.where(*filters)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, patient: Patient) -> Patient:
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def delete(self, patient: Patient) -> None:
        await self.db.delete(patient)
        await self.db.commit()
