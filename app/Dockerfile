FROM python:3.13-slim

WORKDIR /app

# Debian 패키지 목록 업데이트 + 필요한 빌드 도구 설치
RUN apt-get update && apt-get install -y \
    # C/C++ 컴파일러 및 빌드 도구로 pip 패키지 중 native build 필요 시 사용 \
    build-essential \
    # Python C 확장 빌드를 위한 헤더 파일 (일부 라이브러리 필수) \
    python3-dev \
    # cryptography, cffi 등에서 사용하는 Foreign Function Interface 라이브러리 \
    libffi-dev \
    # apt 캐시 제거 -> 이미지 용량 감소 \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 의존성 패지키 관리 파일 복사
COPY pyproject.toml uv.lock ./

# uv 가상환경에 app 의존성 패키지를 설치
RUN uv sync --group app

# 앱 복사
COPY app ./app
# Alembic 마이그레이션 관리 디렉터리 복사
COPY alembic ./alembic
# Alembic 설정 파일 복사
COPY alembic.ini ./
# static files 복사
COPY static ./static

# 실행
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]
