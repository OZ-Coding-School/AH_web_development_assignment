from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.patients import PatientCreate, PatientRead, PatientUpdate, PatientMessage
from app.services.patient_service import PatientService
from app.apis.deps import get_patient_service, get_current_user
from app.models.users import User
from app.core.enums import UserRole, Gender

router = APIRouter(prefix="/patients", tags=["patients"])


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_create: PatientCreate,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user),
):
    # REQ-PTNT-001: 사내 의료인 역할을 가진 유저만 등록 가능
    if current_user.role != UserRole.ADMIN and current_user.department != "medical team":
        # Note: Department.MEDICAL 이 "medical team" 인것 확인됨
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의료인 권한이 필요합니다.")

    return await patient_service.create_patient(patient_create)


@router.get("", response_model=List[PatientRead])
async def get_patients(
    name: Optional[str] = Query(None, description="이름 검색 (부분 일치)"),
    gender: Optional[Gender] = Query(None, description="성별 필터 (M / F)"),
    min_age: Optional[int] = Query(None, description="최소 나이 필터"),
    max_age: Optional[int] = Query(None, description="최대 나이 필터"),
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user),
):
    # REQ-PTNT-002: 로그인 된 사내 개발진, 의료 실무진, 연구진 접근 가능
    return await patient_service.get_patients(name=name, gender=gender, min_age=min_age, max_age=max_age)


@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(
    patient_id: int,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user),
):
    # REQ-PTNT-003: 로그인 된 사내 개발진, 의료 실무진, 연구진 접근 가능
    return await patient_service.get_patient(patient_id)


@router.patch("/{patient_id}", response_model=PatientMessage)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user),
):
    # REQ-PTNT-004: 로그인 된 사내 개발진, 의료 실무진, 연구진 접근 가능
    await patient_service.update_patient(patient_id, patient_update)
    return {"message": "환자 정보가 성공적으로 수정되었습니다."}


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user),
):
    # REQ-PTNT-005: 로그인 된 사내 개발진, 의료 실무진, 연구진 접근 가능
    await patient_service.delete_patient(patient_id)
    return None
