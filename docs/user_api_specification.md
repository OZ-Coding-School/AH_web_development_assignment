# USER API 명세서

## 1. 개요
본 문서는 흉부 X-Ray AI 진단 서비스의 회원(User) 관련 API 명세서입니다. 
요구사항(REQ-USER-001 ~ REQ-USER-008, NFR-USER-001 ~ NFR-USER-002)을 기반으로 작성되었습니다.

## 2. 공통 사항 (Common)
### 2.1. 인증 및 인가 (NFR-USER-002)
- 모든 API는 `Authorization: Bearer {access_token}` 헤더를 통해 인가를 수행합니다. (회원가입, 로그인 제외)
- **JWT 토큰 정책**
    - **Access Token**: 만료 주기 30분
    - **Refresh Token**: 만료 주기 7일
    - **Payload**: `user_id` (최소 식별 정보)
- **보안 사항 (NFR-USER-001)**: 비밀번호 입력은 마스킹 처리되며, 클라이언트에서 보기 기능을 제공해야 합니다.

### 2.2. API 성능 (NFR-USER-002)
- 모든 유저 API는 최대 3초 이내에 로직을 처리하고 응답해야 합니다.

---

## 3. 회원 인증 API

### 3.1. 회원가입 (REQ-USER-001)
- **Endpoint**: `POST /api/v1/users/signup`
- **Description**: 사내 의료인, 실무진, 연구진의 회원가입을 처리합니다.
- **Request Body**

    | 항목 | 타입 | 설명 | 필수여부 | 예시 |
    | :--- | :--- | :--- | :--- | :--- |
    | email | string | 이메일 주소 | Y | user@example.com |
    | password | string | 비밀번호 (마스킹 처리 대상) | Y | password123! |
    | name | string | 이름 | Y | 홍길동 |
    | department | string | 부서 (developer, medical, research) | Y | developer |
    | gender | string | 성별 (M / F) | Y | M |
    | phone_number | string | 휴대폰 번호 | Y | 01012345678 |

- **Response (201 Created)**
    ```json
    {
      "message": "회원가입이 완료되었습니다."
    }
    ```

### 3.2. 로그인 (REQ-USER-002)
- **Endpoint**: `POST /api/v1/users/login`
- **Description**: 이메일과 비밀번호를 입력하여 로그인을 진행하고 JWT 토큰을 발급받습니다.
- **Request Body**

    | 항목 | 타입 | 설명 | 필수여부 | 예시 |
    | :--- | :--- | :--- | :--- | :--- |
    | email | string | 이메일 주소 | Y | user@example.com |
    | password | string | 비밀번호 (마스킹 처리 대상) | Y | password123! |

- **Response (200 OK)**
    ```json
    {
      "access_token": "eyJhbGci...",
      "refresh_token": "eyJhbGci...",
      "token_type": "bearer"
    }
    ```

### 3.3. 로그아웃 (REQ-USER-003)
- **Endpoint**: `POST /api/v1/users/logout`
- **Description**: 로그인 유저의 로그아웃을 진행하며, 완료 후 로그인 페이지로 전환됩니다.
- **Header**: `Authorization: Bearer {access_token}`
- **Response (200 OK)**
    ```json
    {
      "message": "성공적으로 로그아웃되었습니다."
    }
    ```

---

## 4. 마이페이지 API

### 4.1. 내 정보 조회 (REQ-USER-006)
- **Endpoint**: `GET /api/v1/users/me`
- **Description**: 본인의 이름, 이메일, 부서, 성별, 휴대폰 번호, 권한 정보를 확인합니다.
- **Header**: `Authorization: Bearer {access_token}`
- **Response (200 OK)**
    ```json
    {
      "id": 101,
      "name": "홍길동",
      "email": "user@example.com",
      "department": "developer",
      "gender": "M",
      "phone_number": "01012345678",
      "role": "staff"
    }
    ```

### 4.2. 내 정보 수정 (REQ-USER-007)
- **Endpoint**: `PATCH /api/v1/users/me`
- **Description**: 본인의 정보(부서, 휴대폰 번호)를 부분 수정(Partial)합니다.
- **Header**: `Authorization: Bearer {access_token}`
- **Request Body**

    | 항목 | 타입 | 설명 | 필수여부 | 예시 |
    | :--- | :--- | :--- | :--- | :--- |
    | department | string | 부서 (developer, medical, research) | N | medical |
    | phone_number | string | 휴대폰 번호 | N | 01055554444 |

- **Response (200 OK)**
    ```json
    {
      "message": "회원 정보가 수정되었습니다."
    }
    ```

### 4.3. 비밀번호 변경
- **Endpoint**: `PATCH /api/v1/users/me/password`
- **Description**: 현재 비밀번호를 확인한 후 새로운 비밀번호로 변경합니다.
- **Header**: `Authorization: Bearer {access_token}`
- **Request Body**

    | 항목 | 타입 | 설명 | 필수여부 | 예시 |
    | :--- | :--- | :--- | :--- | :--- |
    | current_password | string | 현재 비밀번호 | Y | oldpassword123! |
    | new_password | string | 새 비밀번호 | Y | newpassword456! |

- **Response (200 OK)**
    ```json
    {
      "message": "비밀번호가 변경되었습니다."
    }
    ```

### 4.4. 회원 탈퇴 (REQ-USER-008)
- **Endpoint**: `DELETE /api/v1/users/me`
- **Description**: 회원 탈퇴를 진행하며, DB에서 모든 정보를 즉시 삭제합니다.
- **Header**: `Authorization: Bearer {access_token}`
- **Response (204 No Content)**

---

## 5. 관리자 전용 API (Admin Only)

### 5.1. 회원 목록 조회 (REQ-USER-004)
- **Endpoint**: `GET /api/v1/admin/users`
- **Description**: 모든 회원을 목록으로 조회하며, 검색 및 필터링이 가능합니다.
- **Header**: `Authorization: Bearer {access_token}` (Admin 권한 필요)
- **Query Parameters**

    | 항목 | 타입 | 설명 | 예시 |
    | :--- | :--- | :--- | :--- |
    | query | string | 검색어 (이메일 혹은 이름) | "홍길동" |
    | department | string | 부서 필터 (developer, medical, research) | "medical" |

- **Response (200 OK)**
    ```json
    [
      {
        "id": 101,
        "email": "user@example.com",
        "name": "홍길동",
        "department": "developer",
        "gender": "M",
        "phone_number": "01012345678",
        "is_active": true
      }
    ]
    ```

### 5.2. 회원 권한 변경 (REQ-USER-005)
- **Endpoint**: `PATCH /api/v1/admin/users/role`
- **Description**: 선택된 회원의 권한을 변경합니다. (대기자, 스태프, 어드민)
- **Header**: `Authorization: Bearer {access_token}` (Admin 권한 필요)
- **Request Body**

    | 항목 | 타입 | 설명 | 필수여부 | 예시 |
    | :--- | :--- | :--- | :--- | :--- |
    | user_id | integer | 권한 변경 대상자 ID | Y | 101 |
    | new_role | string | 변경할 권한 (pending, staff, admin) | Y | staff |

- **Response (200 OK)**
    ```json
    {
      "message": "회원 권한이 성공적으로 변경되었습니다."
    }
    ```
