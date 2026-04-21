import logging
import os
import uuid
import json
import asyncio
from typing import Sequence
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis_client import redis_client
from app.models.ai_analysis_results import AIAnalysis
from app.repositories.ai_analysis_repository import AIAnalysisRepository
from app.repositories.medical_record_repository import MedicalRecordRepository


class AIAnalysisService:
    def __init__(self, ai_analysis_repo: AIAnalysisRepository, medical_record_repo: MedicalRecordRepository):
        self.ai_analysis_repo = ai_analysis_repo
        self.medical_record_repo = medical_record_repo
        self.redis_client = redis_client

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
        # settings.MEDIA_DIR (/app/media) + xray-images/filename
        filename = os.path.basename(xray_image.image_url)
        file_path = os.path.join(settings.MEDIA_DIR, "xray-images", filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="이미지 파일을 찾을 수 없습니다.")

        # 중복 요청 방지를 위한 분산 락(Distributed Lock)
        lock_key = f"lock:ai_analysis:{record_id}:{ai_model_name}"
        async with self.redis_client.lock(lock_key, timeout=60):
            # 락 획득 후 이미 결과가 생성되었는지 다시 한번 확인 (Double-checked locking)
            existing_analysis = await self.ai_analysis_repo.get_by_record_id_and_model(record_id, ai_model_name)
            if existing_analysis:
                return existing_analysis

            # Redis 작업 큐에 작업 등록
            unique_id = uuid.uuid4().hex
            task_id = f"task:{record_id}:{ai_model_name}:{unique_id}"
            task_data = {
                "task_id": task_id,
                "record_id": record_id,
                "file_path": file_path,
                "model_name": ai_model_name,
            }

            # 결과 구독을 위한 PubSub 설정
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(task_id)

            # 작업 큐에 등록 (LPUSH)
            await self.redis_client.lpush("ai_task_queue", json.dumps(task_data))

            # 결과 대기 (Timeout 30초 설정)
            try:
                async with asyncio.timeout(30):
                    async for message in pubsub.listen():
                        if message["type"] == "message":
                            prediction_result = json.loads(message["data"])
                            break
            except asyncio.TimeoutError:
                await pubsub.unsubscribe(task_id)
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="AI 분석 시간이 초과되었습니다."
                )
            finally:
                await pubsub.unsubscribe(task_id)

        # AI Analysis Result 결과 모델 인스턴스화
        ai_analysis = AIAnalysis(
            record_id=record_id,
            is_pneumonia=prediction_result["result"]["label"] == "Pneumonia",
            confidence=prediction_result["result"]["confidence"],
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
