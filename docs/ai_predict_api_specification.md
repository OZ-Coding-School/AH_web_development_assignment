# AI 폐렴 예측 API 명세서

본 문서는 사내 의료인, 개발팀, 연구진 유저를 위한 AI 폐렴 예측 및 결과 조회 API 명세서입니다.

## 1. AI 폐렴 예측 수행

진료기록에 등록된 X-ray 이미지를 활용하여 폐렴 여부를 예측합니다. 이미 동일한 모델로 수행된 결과가 있을 경우, 새로 추론하지 않고 기존 결과를 반환합니다.

- **URL:** `/api/v1/medical-records/{record_id}/predict`
- **Method:** `POST`
- **Auth Required:** YES (Bearer Token)
- **Permissions:** Research Team, Medical Team, Dev Team
- **Path Parameters:**
    - `record_id` (integer): 진료기록 고유 ID

### Response
- **Status Code:** `200 OK`
- **Body:**
```json
{
  "id": 1,
  "record_id": 10,
  "is_pneumonia": true,
  "confidence": 98.50,
  "heatmap_url": "/media/heatmaps/sample.png",
  "ai_model": "SimpleCNN-Pneumonia",
  "created_at": "2024-04-14T16:12:00"
}
```

### Error Codes
- `401 Unauthorized`: 인증 토큰 누락 또는 유효하지 않음
- `403 Forbidden`: 접근 권한 없음
- `404 Not Found`: 진료기록을 찾을 수 없거나 이미지 파일이 존재하지 않음
- `400 Bad Request`: 진료기록에 X-ray 이미지가 등록되어 있지 않음

---

## 2. AI 예측 결과 목록 조회

특정 진료기록에 대해 수행된 모든 AI 예측 결과 목록을 조회합니다.

- **URL:** `/api/v1/medical-records/{record_id}/analyses`
- **Method:** `GET`
- **Auth Required:** YES (Bearer Token)
- **Permissions:** Research Team, Medical Team, Dev Team
- **Path Parameters:**
    - `record_id` (integer): 진료기록 고유 ID

### Response
- **Status Code:** `200 OK`
- **Body:**
```json
[
  {
    "id": 2,
    "record_id": 10,
    "is_pneumonia": true,
    "confidence": 98.50,
    "heatmap_url": "/media/heatmaps/sample.png",
    "ai_model": "SimpleCNN-Pneumonia",
    "created_at": "2024-04-14T16:12:00"
  },
  {
    "id": 1,
    "record_id": 10,
    "is_pneumonia": false,
    "confidence": 1.50,
    "heatmap_url": null,
    "ai_model": "Old-Model",
    "created_at": "2024-04-13T10:00:00"
  }
]
```

### Error Codes
- `401 Unauthorized`: 인증 토큰 누락 또는 유효하지 않음
- `403 Forbidden`: 접근 권한 없음
- `404 Not Found`: 진료기록을 찾을 수 없음
