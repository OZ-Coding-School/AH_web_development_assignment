import os
from typing import Sequence
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.ai_analysis_results import AIAnalysis
from app.repositories.ai_analysis_repository import AIAnalysisRepository
from app.repositories.medical_record_repository import MedicalRecordRepository

from worker.model import PneumoniaPredictModel, logger


if not settings.PREDICT_MODEL:
    raise RuntimeError("PREDICT_MODEL is not set in the environment variables.")
pneumonia_model = PneumoniaPredictModel(settings.PREDICT_MODEL)

try:
    pneumonia_model.load()
    logger.info("Pneumonia model pre-loaded successfully during startup.")
except Exception as e:
    # 모델 로드 실패 시 예외 발생으로 서버 실행을 막음
    logger.exception("Failed to load pneumonia model")
    raise RuntimeError("Model loading failed") from e


class AIAnalysisService:
    def __init__(self, ai_analysis_repo: AIAnalysisRepository, medical_record_repo: MedicalRecordRepository):
        self.ai_analysis_repo = ai_analysis_repo
        self.medical_record_repo = medical_record_repo

    async def predict_pneumonia(self, record_id: int) -> AIAnalysis:
        # 진료기록이 존재하는지 확인
        record = await self.medical_record_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="진료기록을 찾을 수 없습니다.")

        # 해당 진료 기록에 대해서 같은 모델을 사용해서 예측을 진행한 내역이 있으면 그대로 리턴
        ai_model_name = settings.PREDICT_MODEL
        existing_analysis = await self.ai_analysis_repo.get_by_record_id_and_model(record_id, ai_model_name)
        if existing_analysis:
            return existing_analysis

        # 흉부 X-Ray 이미지가 존재하는지 확인
        if not record.xray_images:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-ray 이미지가 존재하지 않습니다.")

        xray_image = record.xray_images[0]
        # 실제 이미지 경로로 변환
        # /media/xray-images/... -> app/media/xray-images/...
        file_path = os.path.join("app", xray_image.image_url.lstrip("/"))

        if not os.path.exists(file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="이미지 파일을 찾을 수 없습니다.")

        # 미리 로드된 모델을 활용해 추론
        prediction_result = pneumonia_model.predict(file_path)

        # AI Analysis Result 결과 모델 인스턴스화
        ai_analysis = AIAnalysis(
            record_id=record_id,
            is_pneumonia=prediction_result["label"] == "Pneumonia",
            confidence=prediction_result["confidence"],
            heatmap_url="",
            ai_model=ai_model_name,
        )
        # 결과 리턴
        return await self.ai_analysis_repo.create(ai_analysis)

    async def get_ai_analyses_by_record(self, record_id: int) -> Sequence[AIAnalysis]:
        # 해당 진료기록이 존재하는지 확인
        record = await self.medical_record_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="진료기록을 찾을 수 없습니다.")
        # 진료기록에 대한 ai 예측 목록을 리턴
        return await self.ai_analysis_repo.get_list_by_record_id(record_id)
