from typing import List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.schemas.medical_records import MedicalRecordRead, MedicalRecordListRead, MedicalRecordCreate
from app.schemas.ai_analysis_results import AIAnalysisRead
from app.services.medical_record_service import MedicalRecordService
from app.apis.deps import get_medical_record_service, get_ai_analysis_service, get_current_active_user
from app.services.ai_analysis_service import AIAnalysisService
from app.models.users import User
from app.core.enums import UserRole

router: APIRouter = APIRouter(tags=["medical-records"])


@router.post("/medical-records", response_model=MedicalRecordRead, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    request_data: Annotated[MedicalRecordCreate, Form(..., media_type="multipart/form-data")],
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_active_user),
):
    # REQ-MDR-001: 사내 의료인 역할을 가진 유저만 등록 가능
    if current_user.role != UserRole.ADMIN and current_user.department != "medical team":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의료인 권한이 필요합니다.")

    record = await medical_record_service.create_medical_record(
        **request_data.model_dump(),
        uploader_id=current_user.id,
    )

    # response formatting
    return {
        "id": record.id,
        "patient_id": record.patient_id,
        "chart_number": record.chart_number,
        "symptoms": record.symptoms,
        "xray_image_url": record.xray_images[0].image_url if record.xray_images else None,
        "created_at": record.created_at,
    }


@router.get("/patients/{patient_id}/medical-records", response_model=List[MedicalRecordListRead])
async def get_patient_medical_records(
    patient_id: int,
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_active_user),
):
    # REQ-MDR-003: 로그인 된 사내 개발진, 의료 실무진, 연구진 접근 가능
    return await medical_record_service.get_patient_medical_records(patient_id)


@router.get("/medical-records/{record_id}", response_model=MedicalRecordRead)
async def get_medical_record_detail(
    record_id: int,
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_active_user),
):
    # REQ-MDR-004: 로그인 된 사내 개발진, 의료 실무진, 연구진 접근 가능
    record = await medical_record_service.get_medical_record_detail(record_id)
    return {
        "id": record.id,
        "patient_id": record.patient_id,
        "chart_number": record.chart_number,
        "symptoms": record.symptoms,
        "xray_image_url": record.xray_images[0].image_url if record.xray_images else None,
        "created_at": record.created_at,
    }


@router.post("/medical-records/{record_id}/predict", response_model=AIAnalysisRead)
async def predict_pneumonia(
    record_id: int,
    ai_analysis_service: AIAnalysisService = Depends(get_ai_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    # REQ-PRED-001: 사내 의료인, 개발팀, 어드민 역할을 가진 유저만 접근 가능
    if current_user.role != UserRole.ADMIN and current_user.department not in ["medical team", "dev team"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="AI 분석 권한이 필요합니다.")

    return await ai_analysis_service.predict_pneumonia(record_id)


@router.get("/medical-records/{record_id}/analyses", response_model=List[AIAnalysisRead])
async def get_medical_record_analyses(
    record_id: int,
    ai_analysis_service: AIAnalysisService = Depends(get_ai_analysis_service),
    current_user: User = Depends(get_current_active_user),
):
    # REQ-PRED-002: 사내 의료인, 개발팀, 어드민 역할을 가진 유저만 접근 가능
    if current_user.role != UserRole.ADMIN and current_user.department not in ["medical team", "dev team"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="AI 분석 결과 조회 권한이 필요합니다.")

    return await ai_analysis_service.get_ai_analyses_by_record(record_id)
