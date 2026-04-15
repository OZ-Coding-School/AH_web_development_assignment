/**
 * API 호출을 담당하는 모듈입니다.
 * 각 함수는 백엔드 API 명세의 요구사항 ID를 주석으로 포함합니다.
 */

const apis = {
    // --- Auth & Users ---
    /**
     * 회원가입
     * [REQ-USER-001] 사내 구성원은 이메일, 비밀번호, 이름, 소속 부서, 성별, 전화번호를 입력하여 회원가입을 할 수 있다.
     */
    async signup(userData) {
        return await request('/users/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        }, true);
    },

    /**
     * 로그인
     * [REQ-USER-002] 가입된 이메일과 비밀번호로 로그인을 할 수 있다.
     */
    async login(email, password) {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        return await request('/users/login', {
            method: 'POST',
            body: formData
        }, true);
    },

    /**
     * 토큰 갱신
     * [NFR-USER-001] 로그인 성공 시 Access Token(JSON Body)과 Refresh Token(HTTP-only Cookie)이 발급된다.
     */
    async refresh() {
        return await fetch(`${API_BASE}/users/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
    },

    /**
     * 로그아웃
     * [REQ-USER-003] 로그인된 사용자는 로그아웃을 할 수 있다.
     */
    async logout() {
        return await request('/users/logout', { method: 'POST' });
    },

    /**
     * 내 정보 조회
     * [REQ-USER-006] 로그인된 사용자는 본인의 정보를 조회할 수 있다.
     */
    async getMe() {
        return await request('/users/me');
    },

    /**
     * 내 정보 수정
     * [REQ-USER-007] 로그인된 사용자는 본인의 정보(부서, 전화번호)를 수정할 수 있다.
     */
    async updateMe(userData) {
        return await request('/users/me', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        }, true);
    },

    /**
     * 비밀번호 변경
     * [REQ-USER-008] 로그인된 사용자는 본인의 비밀번호를 변경할 수 있다.
     */
    async updatePassword(passwordData) {
        return await request('/users/me/password', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(passwordData)
        }, true);
    },

    /**
     * 회원 탈퇴
     * [REQ-USER-009] 로그인된 사용자는 회원 탈퇴를 할 수 있다.
     */
    async deleteMe() {
        return await request('/users/me', { method: 'DELETE' });
    },

    // --- Patients ---

    /**
     * 환자 등록
     * [REQ-PTNT-001] 사내 의료인 역할을 가진 유저만 환자를 신규 등록할 수 있다.
     */
    async createPatient(patientData) {
        return await request('/patients', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(patientData)
        });
    },

    /**
     * 환자 목록 조회
     * [REQ-PTNT-002] 로그인된 사내 개발진, 의료 실무진, 연구진은 환자 목록을 조회할 수 있다.
     */
    async getPatients(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await request(`/patients${query ? `?${query}` : ''}`);
    },

    /**
     * 환자 상세 조회
     * [REQ-PTNT-003] 특정 환자의 상세 정보를 조회할 수 있다.
     */
    async getPatient(patientId) {
        return await request(`/patients/${patientId}`);
    },

    /**
     * 환자 정보 수정
     * [REQ-PTNT-004] 특정 환자의 정보를 수정할 수 있다.
     */
    async updatePatient(patientId, patientData) {
        return await request(`/patients/${patientId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(patientData)
        });
    },

    /**
     * 환자 삭제
     * [REQ-PTNT-005] 특정 환자 정보를 삭제할 수 있다.
     */
    async deletePatient(patientId) {
        return await request(`/patients/${patientId}`, { method: 'DELETE' });
    },

    // --- Medical Records ---

    /**
     * 진료 기록 등록
     * [REQ-MDR-001] 사내 의료인 역할을 가진 유저만 환자의 진료 기록을 등록할 수 있다.
     */
    async createMedicalRecord(formData) {
        return await request('/medical-records', {
            method: 'POST',
            body: formData
        });
    },

    /**
     * 환자별 진료 기록 목록 조회
     * [REQ-MDR-002] 특정 환자의 진료 기록 목록을 조회할 수 있다.
     */
    async getPatientMedicalRecords(patientId) {
        return await request(`/patients/${patientId}/medical-records`);
    },

    /**
     * 진료 기록 상세 조회
     * [REQ-MDR-003] 특정 진료 기록의 상세 내용을 조회할 수 있다.
     */
    async getMedicalRecord(recordId) {
        return await request(`/medical-records/${recordId}`);
    },

    // --- AI Prediction ---

    /**
     * AI 폐렴 예측 수행
     * [REQ-PRED-001] 진료기록에 등록된 X-ray 이미지를 활용하여 폐렴 여부를 예측한다.
     */
    async predictPneumonia(recordId) {
        return await request(`/medical-records/${recordId}/predict`, { method: 'POST' });
    },

    /**
     * AI 예측 결과 목록 조회
     * [REQ-PRED-002] 특정 진료기록에 대해 수행된 모든 AI 예측 결과 목록을 조회한다.
     */
    async getMedicalRecordAnalyses(recordId) {
        return await request(`/medical-records/${recordId}/analyses`);
    },

    // --- Admin ---

    /**
     * 전체 유저 목록 조회 (관리자 전용)
     * [REQ-USER-004] 관리자 권한을 가진 유저는 전체 유저 목록을 조회할 수 있다.
     */
    async adminGetUsers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return await request(`/admin/users${query ? `?${query}` : ''}`);
    },

    /**
     * 유저 권한 수정 (관리자 전용)
     * [REQ-USER-005] 관리자 권한을 가진 유저는 다른 유저의 권한을 수정할 수 있다.
     */
    async adminUpdateUserRole(roleData) {
        return await request('/admin/users/role', {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(roleData)
        });
    }
};
