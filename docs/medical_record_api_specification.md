# MEDICAL RECORD API 명세서

## 1. 개요
본 문서는 흉부 X-Ray AI 진단 서비스의 진료기록(Medical Record) 관련 API 명세서입니다. 
요구사항(REQ-MDR-001 ~ REQ-MDR-004, NFR-MDR-001)을 기반으로 작성되었습니다.

## 2. 공통 사항 (Common)
### 2.1. 인증 및 인가
- 모든 API는 `Authorization: Bearer {access_token}` 헤더를 통해 인가를 수행합니다.
- 각 API별로 허용된 역할(Role)을 가진 유저만 접근할 수 있습니다.

### 2.2. API 성능 (NFR-MDR-001)
- 모든 진료기록 API는 최대 3초 이내에 로직을 처리하고 응답해야 합니다.

---

## 3. 진료기록 관리 API

### 3.1. 진료기록 등록 (REQ-MDR-001)
- **Endpoint**: `POST /api/v1/medical-records`
- **Description**: 사내 의료인 역할을 가진 유저가 특정 환자의 진료기록(X-Ray 이미지 포함)을 등록합니다.
- **Header**: `Authorization: Bearer {access_token}` (의료인 권한 필요)
- **Request Body (Multipart/form-data)**

    | 항목 | 타입 | 설명 | 필수여부 | 예시 |
    | :--- | :--- | :--- | :--- | :--- |
    | patient_id | integer | 환자 고유 ID | Y | 1 |
    | chart_number | string | 진료 차트 넘버 | Y | CHART-2024-001 |
    | symptoms | string | 진료된 증상 | Y | 지속적인 기침 및 흉통 |
    | xray_image | file | 흉부 X-Ray 이미지 파일 | Y | xray.png |

- **Response (201 Created)**
    ```json
    {
      "id": 10,
      "patient_id": 1,
      "chart_number": "CHART-2024-001",
      "symptoms": "지속적인 기침 및 흉통",
      "xray_image_url": "/media/xrays/20240413_123456.png",
      "created_at": "2024-04-13T13:00:00"
    }
    ```

### 3.2. 환자별 진료기록 목록 조회 (REQ-MDR-002)
- **Endpoint**: `GET /api/v1/patients/{patient_id}/medical-records`
- **Description**: 특정 환자의 모든 진료기록 목록을 조회합니다.
- **Header**: `Authorization: Bearer {access_token}` (개발진, 의료 실무진, 연구진 접근 가능)
- **Response (200 OK)**
    ```json
    [
      {
        "id": 10,
        "chart_number": "CHART-2024-001",
        "symptoms": "지속적인 기침 및 흉통...",
        "created_at": "2024-04-13T13:00:00"
      },
      {
        "id": 5,
        "chart_number": "CHART-2024-002",
        "symptoms": "환자 증상이 100자를 초과할 경우 생략 표시가 나타납니다. 예를 들면 이와 같이 백 자가 넘어가는...",
        "created_at": "2024-04-10T10:30:00"
      }
    ]
    ```

### 3.3. 진료기록 상세 조회 (REQ-MDR-003)
- **Endpoint**: `GET /api/v1/medical-records/{record_id}`
- **Description**: 특정 진료기록의 상세 정보를 조회합니다.
- **Header**: `Authorization: Bearer {access_token}` (개발진, 의료 실무진, 연구진 접근 가능)
- **Response (200 OK)**
    ```json
    {
      "id": 10,
      "chart_number": "CHART-2024-001",
      "symptoms": "지속적인 기침 및 흉통",
      "xray_image_url": "/media/xrays/20240413_123456.png",
      "created_at": "2024-04-13T13:00:00"
    }
    ```
