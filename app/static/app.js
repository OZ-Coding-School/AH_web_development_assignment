const state = {
    user: null,
    token: localStorage.getItem('token'),
    currentPage: '/'
};

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
        if (state.token) logout();
    }
}

function updateNav() {
    const authLink = document.getElementById('auth-link');
    const adminLinkContainer = document.getElementById('admin-link-container');
    
    if (state.user) {
        document.body.classList.add('logged-in');
        
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
    
    const url = new URL(window.location.origin + path);
    const pathname = url.pathname;
    const searchParams = Object.fromEntries(url.searchParams);
    
    state.currentPage = pathname;
    const app = document.getElementById('app');
    app.innerHTML = '<div class="card">로딩 중...</div>';

    try {
        // PENDING 유저 접근 제한
        const publicPaths = ['/', '/home', '/login', '/signup', '/my-page'];
        if (state.user && state.user.role === 'pending' && !publicPaths.includes(pathname)) {
            utils.showAlert('승인 대기 중인 사용자입니다. 관리자의 승인 이후에 사용가능합니다.', 'error', '접근 제한');
            navigate('/');
            return;
        }

        if (pathname === '/' || pathname === '/home') {
            await pages.renderHome();
        } else if (pathname === '/login') {
            await pages.renderLogin();
        } else if (pathname === '/signup') {
            await pages.renderSignup();
        } else if (pathname === '/patients') {
            await pages.renderPatients(searchParams);
        } else if (pathname === '/patients/create') {
            await pages.renderPatientCreate();
        } else if (pathname.startsWith('/patients/') && pathname.endsWith('/medical-records/create')) {
            const patientId = pathname.split('/')[2];
            await pages.renderRecordCreate(patientId);
        } else if (pathname === '/my-page') {
            pages.renderMyPage();
        } else if (pathname === '/admin/users') {
            await pages.renderAdminUsers(searchParams);
        } else if (pathname.startsWith('/patients/')) {
            const patientId = pathname.split('/')[2];
            await pages.renderPatientDetail(patientId);
        } else if (pathname.startsWith('/medical-records/')) {
            const recordId = pathname.split('/')[2];
            await pages.renderRecordDetail(recordId);
        } else {
            app.innerHTML = '<div class="card"><h2>404</h2><p>페이지를 찾을 수 없습니다.</p></div>';
        }
    } catch (err) {
        app.innerHTML = `<div class="card"><h2>오류</h2><p>${err.message}</p><button onclick="navigate('/')">홈으로</button></div>`;
    }
}

window.onpopstate = () => {
    navigate(window.location.pathname + window.location.search, false);
};

document.addEventListener('DOMContentLoaded', () => {
    checkAuth().then(() => {
        navigate(window.location.pathname + window.location.search, false);
    });
});
