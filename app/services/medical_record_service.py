import os
import uuid
from datetime import datetime
from typing import Sequence
from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.models.medical_records import MedicalRecord, XrayImage
from app.repositories.medical_record_repository import MedicalRecordRepository
from app.repositories.patient_repository import PatientRepository
from app.core.utils import validate_image_extension


class MedicalRecordService:
    def __init__(self, medical_record_repo: MedicalRecordRepository, patient_repo: PatientRepository):
        self.medical_record_repo = medical_record_repo
        self.patient_repo = patient_repo
        self.media_path = settings.MEDIA_DIR / "xray-images"

        # Ensure media directory exists
        if not os.path.exists(self.media_path):
            os.makedirs(self.media_path, exist_ok=True)

    async def create_medical_record(
        self, patient_id: int, chart_number: str, symptoms: str, xray_image: UploadFile, uploader_id: int
    ) -> MedicalRecord:
        # Check if patient exists
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="환자를 찾을 수 없습니다.")

        # Check for duplicate chart number
        existing_record = await self.medical_record_repo.get_by_chart_number(chart_number)
        if existing_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 차트 번호입니다.")

        # Save X-Ray image
        file_ext = validate_image_extension(xray_image.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(self.media_path, unique_filename)

        with open(file_path, "wb") as buffer:
            content = await xray_image.read()
            buffer.write(content)

        # URL path for response
        image_url = f"/media/xray-images/{unique_filename}"

        # Create record
        new_record = MedicalRecord(patient_id=patient_id, chart_number=chart_number, symptoms=symptoms)

        new_xray = XrayImage(uploader_id=uploader_id, image_url=image_url)

        return await self.medical_record_repo.create(new_record, new_xray)

    async def get_patient_medical_records(self, patient_id: int) -> Sequence[MedicalRecord]:
        # Check if patient exists
        patient = await self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="환자를 찾을 수 없습니다.")

        return await self.medical_record_repo.get_by_patient_id(patient_id)

    async def get_medical_record_detail(self, record_id: int) -> MedicalRecord:
        record = await self.medical_record_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="진료기록을 찾을 수 없습니다.")
        return record
