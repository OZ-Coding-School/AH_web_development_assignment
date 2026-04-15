const state = {
    user: null,
    token: localStorage.getItem('token'),
    currentPage: '/'
};

function showAlert(message, type = 'info', title = '알림') {
    const modal = document.getElementById('alert-modal');
    const iconEl = document.getElementById('alert-modal-icon');
    const titleEl = document.getElementById('alert-modal-title');
    const messageEl = document.getElementById('alert-modal-message');
    const closeBtn = document.getElementById('alert-modal-close-btn');

    if (!modal) {
        alert(message);
        return;
    }

    titleEl.innerText = title;
    messageEl.innerText = message;
    
    // 아이콘 설정
    iconEl.className = 'modal-icon ' + type;
    if (type === 'error') iconEl.innerText = '⚠️';
    else if (type === 'success') iconEl.innerText = '✅';
    else iconEl.innerText = 'ℹ️';

    modal.classList.add('show');

    return new Promise((resolve) => {
        closeBtn.onclick = () => {
            modal.classList.remove('show');
            resolve();
        };
        // 모달 바깥 클릭 시 닫기
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
                resolve();
            }
        };
    });
}

const API_BASE = '/api/v1';
const templatesCache = {};

let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
    refreshSubscribers.push(cb);
}

function onTokenRefreshed(token) {
    refreshSubscribers.map(cb => cb(token));
    refreshSubscribers = [];
}

async function request(url, options = {}, skipAlert = false) {
    const headers = { ...options.headers };
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }

    try {
        const response = await fetch(`${API_BASE}${url}`, { ...options, headers });
        
        // 401 Unauthorized 처리 (토큰 만료 시 리프레시 시도)
        if (response.status === 401) {
            // 로그인 요청에서 401은 리프레시 대상이 아님
            if (url === '/users/login') {
                return { status: 401 };
            }
            
            // 토큰이 없는 경우 리프레시 시도 없이 로그아웃
            if (!state.token) {
                logout();
                return null;
            }

            // 이미 리프레시 중이면 대기열에 추가
            if (isRefreshing) {
                return new Promise((resolve) => {
                    subscribeTokenRefresh(token => {
                        headers['Authorization'] = `Bearer ${token}`;
                        resolve(request(url, options, skipAlert));
                    });
                });
            }

            isRefreshing = true;
            try {
                const refreshResponse = await fetch(`${API_BASE}/users/refresh`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (refreshResponse.ok) {
                    const data = await refreshResponse.json();
                    state.token = data.access_token;
                    localStorage.setItem('token', state.token);
                    
                    isRefreshing = false;
                    onTokenRefreshed(state.token);
                    
                    // 원래 요청 재시도
                    headers['Authorization'] = `Bearer ${state.token}`;
                    return await request(url, options, skipAlert);
                } else {
                    // 리프레시 실패 시 로그아웃
                    isRefreshing = false;
                    logout();
                    return null;
                }
            } catch (refreshErr) {
                isRefreshing = false;
                logout();
                return null;
            }
        }
        
        if (!response.ok) {
            let error;
            try {
                error = await response.json();
            } catch (e) {
                error = { detail: '서버 응답 처리 중 오류가 발생했습니다.' };
            }
            
            let msg = error.detail || '요청 중 오류가 발생했습니다.';
            if (Array.isArray(msg)) {
                msg = msg.map(e => {
                    let text = e.msg;
                    text = text.replace(/^Value error, /, '');
                    text = text.replace(/^Field required, /, '');
                    if (text === 'Field required') text = '필수 입력 항목입니다.';
                    return text;
                }).join(', ');
            }

            // 특정 메시지 처리
            const passwordErrorMessage = "비밀번호는 대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다.";
            if (msg.includes(passwordErrorMessage)) {
                msg = passwordErrorMessage;
            } else if (response.status >= 500) {
                msg = "잠시후 다시 시도해주세요.";
            }

            const errObj = new Error(msg);
            errObj.status = response.status;
            throw errObj;
        }
        if (response.status === 204) return null;
        return await response.json();
    } catch (err) {
        if (url !== '/users/login' && !skipAlert) {
            showAlert(err.message, 'error', '오류');
        }
        throw err;
    }
}

async function loadTemplate(name) {
    if (templatesCache[name]) return templatesCache[name];
    const response = await fetch(`/static/templates/${name}.html`);
    const html = await response.text();
    templatesCache[name] = html;
    return html;
}

function formatPhoneNumber(value) {
    if (!value) return value;
    const phoneNumber = value.replace(/[^\d]/g, '');
    const phoneNumberLength = phoneNumber.length;
    if (phoneNumberLength < 4) return phoneNumber;
    if (phoneNumberLength < 8) {
        return `${phoneNumber.slice(0, 3)}-${phoneNumber.slice(3)}`;
    }
    return `${phoneNumber.slice(0, 3)}-${phoneNumber.slice(3, 7)}-${phoneNumber.slice(7, 11)}`;
}

function handlePhoneInput(e) {
    const formattedValue = formatPhoneNumber(e.target.value);
    e.target.value = formattedValue;
}

async function login(email, password) {
    const errorEl = document.getElementById('login-error');
    if (errorEl) errorEl.style.display = 'none';

    try {
        const data = await apis.login(email, password);

        if (data && data.status === 401) {
            if (errorEl) errorEl.style.display = 'block';
            return;
        }

        if (data) {
            state.token = data.access_token;
            localStorage.setItem('token', state.token);
            await checkAuth();
            
            if (state.user && state.user.role === 'pending') {
                navigate('/');
            } else {
                navigate('/patients');
            }
        }
    } catch (err) {
        if (errorEl) {
            errorEl.innerText = err.message || '로그인 중 오류가 발생했습니다.';
            errorEl.style.display = 'block';
        }
    }
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    updateNav();
    navigate('/');
}

async function checkAuth() {
    if (!state.token) {
        // 토큰은 없지만 쿠키(리프레시 토큰)가 있을 수 있으므로 리프레시 시도
        try {
            const refreshResponse = await apis.refresh();
            if (refreshResponse.ok) {
                const data = await refreshResponse.json();
                state.token = data.access_token;
                localStorage.setItem('token', state.token);
            } else {
                return;
            }
        } catch (err) {
            return;
        }
    }
    
    try {
        state.user = await apis.getMe();
        updateNav();
    } catch (err) {
        // request 내부에서 이미 401 처리를 하지만, 
        // 여기서도 실패하면 로그아웃 처리 (이미 request에서 처리되었을 가능성 큼)
        if (state.token) logout();
    }
}

function updateNav() {
    const authLink = document.getElementById('auth-link');
    const adminLinkContainer = document.getElementById('admin-link-container');
    
    if (state.user) {
        document.body.classList.add('logged-in');
        
        // 관리자용 메뉴 표시
        if (state.user.role === 'admin') {
            adminLinkContainer.innerHTML = `<li><a href="/admin/users" onclick="route(event)" class="nav-btn">회원 관리</a></li>`;
        } else {
            adminLinkContainer.innerHTML = '';
        }
        
        authLink.innerHTML = `
            <span class="user-info" onclick="navigate('/my-page')" style="cursor: pointer;">${state.user.name}(${state.user.department})</span>
            <a href="#" onclick="logout()" class="nav-btn logout-btn">로그아웃</a>
        `;
    } else {
        document.body.classList.remove('logged-in');
        adminLinkContainer.innerHTML = '';
        authLink.innerHTML = `<a href="/login" onclick="route(event)" class="nav-btn login-btn">로그인</a>`;
    }
}

function route(event) {
    event.preventDefault();
    const path = event.target.getAttribute('href') || event.currentTarget.getAttribute('href');
    navigate(path);
}

async function navigate(path, pushState = true) {
    if (pushState) {
        window.history.pushState({}, "", path);
    }
    state.currentPage = path;
    const app = document.getElementById('app');
    app.innerHTML = '<div class="card">로딩 중...</div>';

    try {
        // PENDING 유저 접근 제한
        const publicPaths = ['/', '/home', '/login', '/signup', '/my-page'];
        if (state.user && state.user.role === 'pending' && !publicPaths.includes(path)) {
            showAlert('승인 대기 중인 사용자입니다. 관리자의 승인 이후에 사용가능합니다.', 'error', '접근 제한');
            navigate('/');
            return;
        }

        if (path === '/' || path === '/home') {
            await renderHome();
        } else if (path === '/login') {
            await renderLogin();
        } else if (path === '/signup') {
            await renderSignup();
        } else if (path === '/patients') {
            await renderPatients();
        } else if (path === '/patients/create') {
            await renderPatientCreate();
        } else if (path.startsWith('/patients/') && path.endsWith('/medical-records/create')) {
            const patientId = path.split('/')[2];
            await renderRecordCreate(patientId);
        } else if (path === '/my-page') {
            renderMyPage();
        } else if (path === '/admin/users') {
            await renderAdminUsers();
        } else if (path.startsWith('/patients/')) {
            const patientId = path.split('/')[2];
            await renderPatientDetail(patientId);
        } else if (path.startsWith('/medical-records/')) {
            const recordId = path.split('/')[2];
            await renderRecordDetail(recordId);
        } else {
            app.innerHTML = '<div class="card"><h2>404</h2><p>페이지를 찾을 수 없습니다.</p></div>';
        }
    } catch (err) {
        app.innerHTML = `<div class="card"><h2>오류</h2><p>${err.message}</p><button onclick="navigate('/')">홈으로</button></div>`;
    }
}

async function renderHome() {
    const html = await loadTemplate('home');
    const app = document.getElementById('app');
    app.innerHTML = html;
    
    const actions = document.getElementById('home-actions');
    if (!state.user) {
        actions.innerHTML = '<button onclick="navigate(\'/login\')">로그인하여 시작하기</button>';
    } else if (state.user.role === 'pending') {
        actions.innerHTML = '<p>관리자의 승인을 기다리는 중입니다.</p>';
    } else {
        actions.innerHTML = '<button onclick="navigate(\'/patients\')">환자 목록 보기</button>';
    }
}

async function renderLogin() {
    const html = await loadTemplate('login');
    document.getElementById('app').innerHTML = html;
}

async function renderSignup() {
    const html = await loadTemplate('signup');
    document.getElementById('app').innerHTML = html;
    
    const phoneInput = document.getElementById('signup-phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', handlePhoneInput);
    }
}

async function renderPatients(params = {}) {
    const patients = await apis.getPatients(params);
    const html = await loadTemplate('patients');
    const app = document.getElementById('app');
    app.innerHTML = html;

    // 필드 값 복원 (검색 후에도 입력값이 유지되도록)
    if (params.name) document.getElementById('search-name').value = params.name;
    if (params.gender) document.getElementById('filter-gender').value = params.gender;
    if (params.min_age) document.getElementById('filter-min-age').value = params.min_age;
    if (params.max_age) document.getElementById('filter-max-age').value = params.max_age;
    
    const listBody = document.getElementById('patients-list');
    listBody.innerHTML = patients.map(p => `
        <tr>
            <td>${p.id}</td>
            <td>${p.name}</td>
            <td>${p.age}</td>
            <td>${p.gender === 'male' ? '남성' : '여성'}</td>
            <td>${formatPhoneNumber(p.phone_number)}</td>
            <td><button onclick="navigate('/patients/${p.id}')">상세보기</button></td>
        </tr>
    `).join('');
}

async function renderPatientCreate() {
    const html = await loadTemplate('patient-create');
    document.getElementById('app').innerHTML = html;
    
    const phoneInput = document.getElementById('phone_number');
    if (phoneInput) {
        phoneInput.addEventListener('input', handlePhoneInput);
    }
}

async function renderPatientDetail(patientId) {
    const patient = await apis.getPatient(patientId);
    const records = await apis.getPatientMedicalRecords(patientId);
    const html = await loadTemplate('patient-detail');
    const app = document.getElementById('app');
    app.innerHTML = html;
    
    // 환자 정보 표시
    document.getElementById('patient-name').innerText = `${patient.name} (${patient.gender === 'male' ? '남성' : '여성'})`;
    document.getElementById('patient-info').innerText = `나이: ${patient.age}세 | 연락처: ${formatPhoneNumber(patient.phone_number)}`;
    
    // 수정 폼 초기값 설정
    document.getElementById('update-name').value = patient.name;
    document.getElementById('update-phone').value = formatPhoneNumber(patient.phone_number);
    
    const updatePhoneInput = document.getElementById('update-phone');
    if (updatePhoneInput) {
        updatePhoneInput.addEventListener('input', handlePhoneInput);
    }
    
    // 버튼 이벤트 바인딩
    document.getElementById('add-record-btn').onclick = () => navigate(`/patients/${patientId}/medical-records/create`);
    
    // 상세 페이지 전용 상태 (ID 저장)
    state.currentPatientId = patientId;

    const listBody = document.getElementById('records-list');
    listBody.innerHTML = records.map(r => `
        <tr>
            <td>${r.id}</td>
            <td>${r.chart_number}</td>
            <td>${r.symptoms}</td>
            <td>${new Date(r.created_at).toLocaleString()}</td>
            <td><button onclick="navigate('/medical-records/${r.id}')">상세보기</button></td>
        </tr>
    `).join('');
}

async function renderRecordCreate(patientId) {
    const html = await loadTemplate('record-create');
    const app = document.getElementById('app');
    app.innerHTML = html;
    
    const imageInput = document.getElementById('xray_image');
    const previewContainer = document.getElementById('image-preview-container');

    imageInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                previewContainer.innerHTML = `<img src="${event.target.result}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">`;
            };
            reader.readAsDataURL(file);
        } else {
            previewContainer.innerHTML = '<p>이미지 미리보기가 여기에 표시됩니다.</p>';
        }
    };

    document.getElementById('record-create-form').onsubmit = (e) => handleRecordCreate(e, patientId);
    document.getElementById('cancel-btn').onclick = () => navigate(`/patients/${patientId}`);
}

async function renderRecordDetail(recordId) {
    const record = await apis.getMedicalRecord(recordId);
    const analyses = await apis.getMedicalRecordAnalyses(recordId);
    const html = await loadTemplate('record-detail');
    const app = document.getElementById('app');
    app.innerHTML = html;
    
    document.getElementById('record-id').innerText = record.id;
    document.getElementById('chart-number').innerText = record.chart_number;
    document.getElementById('symptoms-text').innerText = record.symptoms;
    document.getElementById('created-at').innerText = new Date(record.created_at).toLocaleString();
    document.getElementById('xray-img').src = record.xray_image_url;
    
    document.getElementById('predict-btn').onclick = () => handlePredict(recordId);
    document.getElementById('back-to-patient-btn').onclick = () => navigate(`/patients/${record.patient_id}`);
    
    const analysisList = document.getElementById('analysis-list');
    if (analyses.length === 0) {
        analysisList.innerHTML = '<p>저장된 예측 결과가 없습니다.</p>';
    } else {
        analysisList.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>수행 일시</th>
                        <th>폐렴 여부</th>
                        <th>Confidence</th>
                        <th>사용 모델</th>
                    </tr>
                </thead>
                <tbody>
                    ${analyses.map(a => `
                        <tr class="${a.is_pneumonia ? 'result-positive' : 'result-negative'}">
                            <td>${new Date(a.created_at).toLocaleString()}</td>
                            <td><strong>${a.is_pneumonia ? 'Positive' : 'Negative'}</strong></td>
                            <td>${a.confidence}%</td>
                            <td>${a.ai_model}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
}

async function renderMyPage() {
    const html = await loadTemplate('my-page');
    const app = document.getElementById('app');
    app.innerHTML = html;

    // 현재 사용자 정보 표시
    document.getElementById('me-email').innerText = state.user.email;
    document.getElementById('me-name-display').innerText = state.user.name;
    document.getElementById('me-department-display').innerText = state.user.department;
    document.getElementById('me-gender-display').innerText = state.user.gender === 'male' ? '남성' : '여성';
    document.getElementById('me-phone-display').innerText = formatPhoneNumber(state.user.phone_number);
    document.getElementById('me-role-display').innerText = state.user.role;

    // 수정 폼 초기값 설정
    document.getElementById('update-me-department').value = state.user.department;
    document.getElementById('update-me-phone').value = formatPhoneNumber(state.user.phone_number);
    
    const mePhoneInput = document.getElementById('update-me-phone');
    if (mePhoneInput) {
        mePhoneInput.addEventListener('input', handlePhoneInput);
    }

    // 이벤트 바인딩
    document.getElementById('update-me-form').onsubmit = handleUpdateMe;
    document.getElementById('update-password-form').onsubmit = handleUpdatePassword;
    document.getElementById('delete-me-btn').onclick = handleDeleteMe;
}

async function renderAdminUsers(params = {}) {
    const users = await apis.adminGetUsers(params);
    const html = await loadTemplate('admin-users');
    const app = document.getElementById('app');
    app.innerHTML = html;

    // 필드 값 복원
    if (params.query) document.getElementById('admin-search-query').value = params.query;
    if (params.department) document.getElementById('admin-filter-dept').value = params.department;

    const listBody = document.getElementById('admin-users-list');
    listBody.innerHTML = users.map(u => `
        <tr>
            <td>${u.id}</td>
            <td>${u.name}</td>
            <td>${u.email}</td>
            <td>${u.department}</td>
            <td>${formatPhoneNumber(u.phone_number)}</td>
            <td>
                <select onchange="handleRoleUpdate(${u.id}, this.value)" ${u.id === state.user.id ? 'disabled' : ''}>
                    <option value="pending" ${u.role === 'pending' ? 'selected' : ''}>승인대기</option>
                    <option value="staff" ${u.role === 'staff' ? 'selected' : ''}>일반회원</option>
                    <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>관리자</option>
                </select>
            </td>
            <td>${u.is_active ? '<span class="status-badge success">활성</span>' : '<span class="status-badge error">비활성</span>'}</td>
        </tr>
    `).join('');
}

function handleAdminSearch() {
    const params = {
        query: document.getElementById('admin-search-query').value,
        department: document.getElementById('admin-filter-dept').value
    };
    renderAdminUsers(params);
}

function resetAdminSearch() {
    renderAdminUsers({});
}

async function handleRoleUpdate(userId, newRole) {
    try {
        await apis.adminUpdateUserRole({ user_id: userId, new_role: newRole });
        showAlert('권한이 변경되었습니다.', 'success');
        // 목록 다시 로드하여 최신 상태 반영
        handleAdminSearch();
    } catch (err) {
        showAlert(`권한 변경 실패: ${err.message}`, 'error');
    }
}

async function handleUpdateMe(e) {
    e.preventDefault();
    const data = {
        department: document.getElementById('update-me-department').value,
        phone_number: document.getElementById('update-me-phone').value.replace(/[^\d]/g, '')
    };

    const phoneErrorEl = document.getElementById('update-me-phone-error');
    if (phoneErrorEl) phoneErrorEl.style.display = 'none';

    try {
        await apis.updateMe(data);
        showAlert('회원 정보가 수정되었습니다.', 'success');
        await checkAuth(); // 상태 갱신
        renderMyPage(); // 화면 갱신
    } catch (err) {
        let msg = err.message;
        if (err.status === 500) {
            msg = '잠시 후 다시시도해주세요.';
        }
        showAlert(msg, 'error', '수정 실패');
    }
}

async function handleUpdatePassword(e) {
    e.preventDefault();
    const data = {
        current_password: document.getElementById('old-password').value,
        new_password: document.getElementById('new-password').value
    };

    try {
        await apis.updatePassword(data);
        showAlert('비밀번호가 변경되었습니다.', 'success');
        e.target.reset();
    } catch (err) {
        let msg = err.message;
        if (err.status === 400) {
            msg = '비밀번호는 "대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다."';
        } else if (err.status === 500) {
            msg = '잠시 후 다시시도해주세요.';
        }
        showAlert(msg, 'error', '비밀번호 변경 실패');
    }
}

async function handleDeleteMe() {
    if (!confirm('정말로 탈퇴하시겠습니까? 모든 데이터가 삭제됩니다.')) return;

    try {
        await apis.deleteMe();
        showAlert('탈퇴 처리가 완료되었습니다.', 'success');
        logout();
    } catch (err) {
        showAlert(`탈퇴 처리 실패: ${err.message}`, 'error');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    await login(email, password);
}

async function handleSignup(e) {
    e.preventDefault();
    const userData = {
        email: document.getElementById('signup-email').value,
        name: document.getElementById('signup-name').value,
        department: document.getElementById('signup-department').value,
        gender: document.getElementById('signup-gender').value,
        phone_number: document.getElementById('signup-phone').value.replace(/[^\d]/g, ''),
        password: document.getElementById('signup-password').value
    };

    const phoneErrorEl = document.getElementById('signup-phone-error');
    if (phoneErrorEl) phoneErrorEl.style.display = 'none';

    try {
        await apis.signup(userData);
        showAlert('회원가입이 완료되었습니다. 로그인해주세요.', 'success');
        navigate('/login');
    } catch (err) {
        let msg = err.message;
        if (err.status === 400 && (msg.includes('비밀번호') || msg.includes('password'))) {
            msg = '비밀번호는 "대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다."';
        }
        if (err.status === 500) {
            msg = '잠시 후 다시시도해주세요.';
        }
        showAlert(msg, 'error', '가입 실패');
    }
}

async function handlePatientCreate(e) {
    e.preventDefault();
    const patientData = {
        name: document.getElementById('name').value,
        age: parseInt(document.getElementById('age').value),
        gender: document.getElementById('gender').value,
        phone_number: document.getElementById('phone_number').value.replace(/[^\d]/g, '')
    };
    
    try {
        await apis.createPatient(patientData);
        
        showAlert('환자가 등록되었습니다.', 'success');
        navigate('/patients');
    } catch (err) {
        showAlert(`환자 등록 실패: ${err.message}`, 'error');
    }
}

function handleSearch() {
    const params = {
        name: document.getElementById('search-name').value,
        gender: document.getElementById('filter-gender').value,
        min_age: document.getElementById('filter-min-age').value,
        max_age: document.getElementById('filter-max-age').value
    };
    renderPatients(params);
}

function resetSearch() {
    renderPatients({});
}

async function handleRecordCreate(e, patientId) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('patient_id', patientId);
    formData.append('chart_number', document.getElementById('chart_number').value);
    formData.append('symptoms', document.getElementById('symptoms').value);
    formData.append('xray_image', document.getElementById('xray_image').files[0]);

    try {
        await apis.createMedicalRecord(formData);

        showAlert('진료 기록이 등록되었습니다.', 'success');
        navigate(`/patients/${patientId}`);
    } catch (err) {
        showAlert(`진료 기록 등록 실패: ${err.message}`, 'error');
    }
}

// 환자 정보 수정 및 삭제 관련 함수 추가
function openUpdateModal() {
    document.getElementById('update-modal').classList.add('show');
}

function closeUpdateModal() {
    document.getElementById('update-modal').classList.remove('show');
}

async function handlePatientUpdate(e) {
    e.preventDefault();
    const patientId = state.currentPatientId;
    const updateData = {
        name: document.getElementById('update-name').value,
        phone_number: document.getElementById('update-phone').value.replace(/[^\d]/g, '')
    };

    try {
        await apis.updatePatient(patientId, updateData);
        showAlert('환자 정보가 수정되었습니다.', 'success');
        closeUpdateModal();
        renderPatientDetail(patientId);
    } catch (err) {
        showAlert(`환자 정보 수정 실패: ${err.message}`, 'error');
    }
}

function confirmDeletePatient() {
    document.getElementById('delete-modal').classList.add('show');
}

function closeDeleteModal() {
    document.getElementById('delete-modal').classList.remove('show');
}

async function handlePatientDelete() {
    const patientId = state.currentPatientId;
    try {
        await apis.deletePatient(patientId);
        showAlert('환자 정보와 관련 데이터가 모두 삭제되었습니다.', 'success');
        closeDeleteModal();
        navigate('/patients');
    } catch (err) {
        showAlert(`환자 삭제 실패: ${err.message}`, 'error');
    }
}

async function handlePredict(recordId) {
    try {
        await apis.predictPneumonia(recordId);
        showAlert('AI 예측이 완료되었습니다.', 'success');
        navigate(`/medical-records/${recordId}`, false); // 결과 갱신을 위해 재로드 (히스토리 중복 방지)
    } catch (err) {
        showAlert(`AI 예측 실패: ${err.message}`, 'error');
    }
}

window.onpopstate = () => {
    navigate(window.location.pathname, false);
};

document.addEventListener('DOMContentLoaded', () => {
    checkAuth().then(() => {
        navigate(window.location.pathname, false);
    });
});
