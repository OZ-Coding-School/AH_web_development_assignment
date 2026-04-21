FROM python:3.13-slim

WORKDIR /app

# 빌드 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 의존성 복사 및 설치
COPY pyproject.toml uv.lock ./

# uv 가상환경에 의존성 패키지를 설치
RUN uv sync --group ai

# 소스 코드
COPY ./worker ./worker
# 실행 명령
CMD ["uv", "run", "python", "-m", "worker.main"]
