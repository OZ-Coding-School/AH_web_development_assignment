# PATIENT API 명세서

## 1. 개요
본 문서는 흉부 X-Ray AI 진단 서비스의 환자(Patient) 관련 API 명세서입니다. 
요구사항(REQ-PTNT-001 ~ REQ-PTNT-004, NFR-PTNT-001)을 기반으로 작성되었습니다.

## 2. 공통 사항 (Common)
### 2.1. 인증 및 인가
- 모든 API는 `Authorization: Bearer {access_token}` 헤더를 통해 인가를 수행합니다.
- 각 API별로 허용된 역할(Role)을 가진 유저만 접근할 수 있습니다.

### 2.2. API 성능 (NFR-PTNT-001)
- 모든 환자 API는 최대 3초 이내에 로직을 처리하고 응답해야 합니다.

---

## 3. 환자 관리 API

### 3.1. 환자 정보 등록 (REQ-PTNT-001)
- **Endpoint**: `POST /api/v1/patients`
- **Description**: 사내 의료인 역할을 가진 유저가 새로운 환자 정보를 등록합니다.
- **Header**: `Authorization: Bearer {access_token}` (의료인 권한 필요)
- **Request Body**

    | 항목 | 타입 | 설명 | 필수여부 | 예시 |
    | :--- | :--- | :--- | :--- | :--- |
    | name | string | 이름 | Y | 홍길동 |
    | age | integer | 나이 | Y | 45 |
    | gender | string | 성별 (M / F) | Y | M |
    | phone_number | string | 연락처 (휴대폰 번호) | Y | 01012345678 |

- **Response (201 Created)**
    ```json
    {
      "id": 1,
      "name": "홍길동",
      "age": 45,
      "gender": "M",
      "phone_number": "01012345678",
      "created_at": "2024-04-13T13:00:00",
      "updated_at": "2024-04-13T13:00:00"
    }
    ```

### 3.2. 환자 목록 조회 (REQ-PTNT-002)
- **Endpoint**: `GET /api/v1/patients`
- **Description**: 등록된 환자 정보를 목록으로 조회합니다. 이름 검색 및 성별, 나이 범위 필터링을 제공합니다.
- **Header**: `Authorization: Bearer {access_token}` (개발진, 의료 실무진, 연구진 접근 가능)
- **Query Parameters**

    | 항목 | 타입 | 설명 | 예시 |
    | :--- | :--- | :--- | :--- |
    | name | string | 이름 검색 (부분 일치) | "홍길동" |
    | gender | string | 성별 필터 (M / F) | "M" |
    | min_age | integer | 최소 나이 필터 | 20 |
    | max_age | integer | 최대 나이 필터 | 50 |

- **Response (200 OK)**
    ```json
    [
      {
        "id": 1,
        "name": "홍길동",
        "age": 45,
        "gender": "M",
        "phone_number": "01012345678",
        "created_at": "2024-04-13T13:00:00",
        "updated_at": "2024-04-13T13:00:00"
      }
    ]
    ```

### 3.3. 환자 정보 수정 (REQ-PTNT-003)
- **Endpoint**: `PATCH /api/v1/patients/{patient_id}`
- **Description**: 특정 환자의 정보를 수정합니다. 이름과 연락처만 수정 가능합니다.
- **Header**: `Authorization: Bearer {access_token}` (개발진, 의료 실무진, 연구진 접근 가능)
- **Request Body**

    | 항목 | 타입 | 설명 | 필수여부 | 예시 |
    | :--- | :--- | :--- | :--- | :--- |
    | name | string | 이름 | N | 홍길순 |
    | phone_number | string | 연락처 (휴대폰 번호) | N | 01098765432 |

- **Response (200 OK)**
    ```json
    {
      "message": "환자 정보가 성공적으로 수정되었습니다."
    }
    ```

### 3.4. 환자 정보 삭제 (REQ-PTNT-004)
- **Endpoint**: `DELETE /api/v1/patients/{patient_id}`
- **Description**: 특정 환자의 정보를 삭제합니다. 삭제 시 해당 환자와 관련된 진료기록 및 X-Ray 이미지도 함께 영구 삭제됩니다.
- **Header**: `Authorization: Bearer {access_token}` (개발진, 의료 실무진, 연구진 접근 가능)
- **Response (204 No Content)**
