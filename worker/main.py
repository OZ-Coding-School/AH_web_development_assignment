import json
import os
import redis

from dataclasses import dataclass, asdict
from datetime import datetime
from enum import StrEnum

from worker.model import PneumoniaPredictModel, logger
from worker.redis_client import redis_client as r

TASK_QUEUE_NAME = "ai_task_queue"
PROCESSING_QUEUE_NAME = "ai_processing_queue"


class ProcessingStatus(StrEnum):
    PROCESSING = "processing"  # 작업 처리상태 진입
    PREDICT_COMPLETED = "predict_completed"  # 추론까지 완료된 상태
    PUBLISHED = "published"  # 추론 및 결과 전송 완료 상태


@dataclass
class TaskMetadata:
    status: ProcessingStatus
    started_at: str

    def to_dict(self):
        return asdict(self)


@dataclass
class TaskData:
    task_id: str
    record_id: int
    file_path: str
    model_name: str


def set_processing_metadata(redis_client: redis.Redis, task_id: str, metadata: TaskMetadata):
    redis_client.hset(task_id, mapping=metadata.to_dict())


def recover_unfinished_processing_task(redis_client: redis.Redis, timeout: int = 60):
    logger.info("Recovering unfinished tasks...")
    now = int(datetime.now().timestamp())
    tasks = redis_client.lrange(PROCESSING_QUEUE_NAME, 0, -1)
    # Processing Queue를 순회하며
    for task in tasks:
        task_data = json.loads(task)
        task_id = task_data.get("task_id")

        # 메타데이터를 확인
        meta = redis_client.hgetall(task_id)
        started_at = int(meta.get("started_at", now))

        # Publish 되지 않은 작업들 중에서 timeout이 지난 Task들을 미완료처리 작업으로 간주하고 Task Queue에 복구
        if (
            meta.get("status") in [ProcessingStatus.PROCESSING.value, ProcessingStatus.PREDICT_COMPLETED.value]
            and now - started_at > timeout
        ):
            logger.info(f"Recovering stale task {task_id}")

            redis_client.lpush(TASK_QUEUE_NAME, task)
            redis_client.lrem(PROCESSING_QUEUE_NAME, 1, task)


def extract_task_data(task: str) -> TaskData:
    data = TaskData(**json.loads(task))
    if not data.task_id or not data.record_id or not data.file_path or not data.model_name:
        raise ValueError("Invalid task data: missing required fields")
    return data


def main():
    # 모델을 미리 메모리에 캐시
    models = {"pneumonia_model_v1": PneumoniaPredictModel("pneumonia_model_v1").load()}

    logger.info("Worker started. Waiting for tasks...")
    # 시작 시 미완료 태스크 복구 호출 (timeout 설정 필요)
    recover_unfinished_processing_task(r)
    while True:
        try:
            # 작업 큐에서 태스크 가져오기 (Blocking Pop)
            # BRPOP은 리스트의 끝에서 데이터를 가져옴과 동시에 LPUSH로 가져온 태스크를 프로세싱 큐에 집어넣음
            task = r.brpoplpush(TASK_QUEUE_NAME, PROCESSING_QUEUE_NAME, timeout=5)

            if not task:
                continue

            started_at = str(int(datetime.now().timestamp()))
            logger.info(f"Received task and Added task to processing queue: {task}, started_at: {started_at}")

            # Task 처리에 필요한 데이터 추출
            task_data = extract_task_data(task)
            # 해시데이터로 작업중 상태, 시작시간을 저장
            set_processing_metadata(
                r, task_data.task_id, TaskMetadata(status=ProcessingStatus.PROCESSING, started_at=started_at)
            )
            logger.info(f"Processing task {task_data.task_id} for record {task_data.record_id}")

            try:
                # 모델명 유효성 확인 후 존재하지않는 모델명일때는 raise
                if task_data.model_name not in models:
                    logger.error(f"Invalid model name: {task_data.model_name}")
                    raise ValueError(f"Invalid model name: {task_data.model_name}")

                model = models[task_data.model_name]

                # 이미지 파일 존재확인
                if not os.path.exists(task_data.file_path):
                    logger.error(f"File not found: {task_data.file_path}")
                    raise FileNotFoundError(f"File not found: {task_data.file_path}")

                # 추론 수행
                prediction_result = model.predict(task_data.file_path)
                # 해시데이터로 예측 완료 상태, 시작시간을 저장
                set_processing_metadata(
                    r, task_data.task_id, TaskMetadata(status=ProcessingStatus.PREDICT_COMPLETED, started_at=started_at)
                )
                logger.info("Prediction Completed.")

                # 결과 Publish
                r.publish(task_data.task_id, json.dumps({"status": "success", "result": prediction_result}))
                # 해시데이터로 작업처리 완료 상태, 시작시간을 저장
                set_processing_metadata(
                    r, task_data.task_id, TaskMetadata(status=ProcessingStatus.PUBLISHED, started_at=started_at)
                )
                # client의 subscription은 1분 이내로 제한하여 고아 응답 객체가 생기는걸 방지
                r.expire(task_data.task_id, time=60)
                logger.info("Prediction Result Published to channel.")
                logger.info(f"Task {task_data.task_id} completed.")
            except Exception as e:
                logger.error(f"Error during processing task for {task_data.task_id}: {e}")
                # 예외 상황을 Publish
                r.publish(task_data.task_id, json.dumps({"status": "error", "message": str(e)}))
                # 에러에 대한 처리 후 task의 메타데이터를 즉시 삭제 (복구 로직에서 되살리지 않기 위함)
                r.delete(task_data.task_id)
                logger.info(f"Task {task_data.task_id} failed. Deleted metadata.")
            finally:
                # 워커가 갑작스레 꺼진 상황을 제외하고는 예외처리와 결과처리가 이루어지고 있으므로 processing queue에서 제거
                r.lrem(PROCESSING_QUEUE_NAME, 1, task)
                logger.info(f"Removed task {task_data.task_id} from processing queue.")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")


if __name__ == "__main__":
    main()
