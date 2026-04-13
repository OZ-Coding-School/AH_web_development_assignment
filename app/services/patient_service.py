from typing import Optional, Sequence
from fastapi import HTTPException, status
from app.models.patients import Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas.patients import PatientCreate, PatientUpdate
from app.core.enums import Gender


class PatientService:
    def __init__(self, patient_repo: PatientRepository):
        self.patient_repo = patient_repo

    async def create_patient(self, patient_create: PatientCreate) -> Patient:
        new_patient = Patient(
            name=patient_create.name,
            age=patient_create.age,
            gender=patient_create.gender,
            phone_number=patient_create.phone_number,
        )
        return await self.patient_repo.create(new_patient)

    async def get_patient(self, patient_id: int) -> Patient:
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="환자를 찾을 수 없습니다.")
        return patient

    async def get_patients(
        self,
        name: Optional[str] = None,
        gender: Optional[Gender] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None,
    ) -> Sequence[Patient]:
        return await self.patient_repo.get_patients(name=name, gender=gender, min_age=min_age, max_age=max_age)

    async def update_patient(self, patient_id: int, patient_update: PatientUpdate) -> Patient:
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="환자를 찾을 수 없습니다.")

        if patient_update.name is not None:
            patient.name = patient_update.name
        if patient_update.phone_number is not None:
            patient.phone_number = patient_update.phone_number

        return await self.patient_repo.update(patient)

    async def delete_patient(self, patient_id: int) -> None:
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="환자를 찾을 수 없습니다.")
        await self.patient_repo.delete(patient)
