# Story 6.5: Railway 배포 설정

Status: done

## Story

As a developer,
I want all three services deployed to Railway as independent services,
so that the application is accessible for portfolio demonstration.

## Acceptance Criteria

1. carrot-api, carrot-web, carrot-admin 각각 Railway 서비스로 독립 배포 가능한 Dockerfile이 존재한다
2. carrot-api 배포 시 Alembic 마이그레이션이 자동 실행된 후 FastAPI가 기동된다
3. carrot-api는 `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`, `JWT_SECRET`, `ALLOWED_ORIGINS` 환경 변수로 구성된다
4. carrot-web 및 carrot-admin은 `NEXT_PUBLIC_API_URL` 빌드 시 환경 변수로 API URL을 받는다
5. carrot-api CORS는 `ALLOWED_ORIGINS` 환경 변수에서 추가 오리진을 읽어 Railway 도메인을 허용한다
6. Next.js 앱은 `output: 'standalone'` 모드로 빌드되어 Docker 컨테이너에서 실행 가능하다

## Tasks / Subtasks

- [x] Task 1: carrot-api/Dockerfile + .dockerignore 생성 (AC: #1, #2)
- [x] Task 2: carrot-api/app/core/config.py 수정 — ALLOWED_ORIGINS 설정 추가 (AC: #3, #5)
- [x] Task 3: carrot-api/app/main.py 수정 — CORS에 ALLOWED_ORIGINS 환경 변수 반영 (AC: #5)
- [x] Task 4: carrot-web/next.config.ts + Dockerfile + .dockerignore 생성/수정 (AC: #1, #4, #6)
- [x] Task 5: carrot-admin/next.config.ts + Dockerfile + .dockerignore 생성/수정 (AC: #1, #4, #6)
- [x] Task 6: 배포 검증 — TypeScript 빌드 + Python import 체크 + CORS 단위 테스트 (AC: #3, #5, #6)

### Review Findings (2026-05-30)

- [x] [Review][Patch] `.env`/`.env.production` 누락 — carrot-web/admin .dockerignore에 추가 [carrot-web/.dockerignore, carrot-admin/.dockerignore]
- [x] [Review][Patch] 테스트가 타입만 확인 → 기본값 `""` 어써션 강화 [test_cors_config.py]
- [x] [Review][Patch] `ALLOWED_ORIGINS=*` 와일드카드 guard 추가 [carrot-api/app/main.py]
- [x] [Review][Defer] DATABASE_URL +asyncpg 접두사 필요 — deferred, 운영 문서/ops 관심사
- [x] [Review][Defer] uv 버전 미고정 — deferred, 포트폴리오 범위
- [x] [Review][Defer] 비루트 사용자 없음 — deferred, 보안 강화 포트폴리오 이후
- [x] [Review][Defer] NEXT_PUBLIC_API_URL 미설정 시 빈 문자열 — deferred, ops 빌드 절차로 관리

## Dev Notes

---

### 배포 아키텍처

Railway에 3개 독립 서비스:
- `carrot-api` → FastAPI (PORT 환경변수 사용)
- `carrot-web` → Next.js 사용자 웹
- `carrot-admin` → Next.js 관리자 웹

Railway는 Dockerfile이 있으면 자동으로 Docker 빌드를 사용한다.

---

### Task 1: carrot-api/Dockerfile + .dockerignore

**carrot-api/Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY . .

EXPOSE 8000

CMD ["/bin/sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

**핵심:**
- `uv sync --no-dev --frozen` → `uv.lock` 고정 버전 설치, dev 의존성 제외
- `uv run` → 프로젝트 venv 활성화 후 실행
- Railway는 `PORT` 환경 변수를 자동 주입, `${PORT:-8000}` 폴백 패턴
- `alembic upgrade head` → 서버 기동 전 마이그레이션 자동 실행

**carrot-api/.dockerignore:**
```
.venv/
__pycache__/
*.pyc
.pytest_cache/
tests/
.env
.env.local
```

---

### Task 2: carrot-api/app/core/config.py

`ALLOWED_ORIGINS` 필드를 추가합니다 (기존 필드 **모두 유지**):

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30일
    ALLOWED_ORIGINS: str = ""  # 쉼표 구분 추가 오리진 (Railway 배포 URL)


settings = Settings()
```

`ALLOWED_ORIGINS`는 기본값 `""` (빈 문자열) → 로컬에서는 아무 효과 없음.

---

### Task 3: carrot-api/app/main.py

CORS 설정을 환경 변수 기반으로 확장합니다.

**현재 상태 (수정 전):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # carrot-web 로컬
        "http://localhost:3001",   # carrot-admin 로컬
    ],
    ...
)
```

**수정 후:**
```python
from app.core.config import settings

_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]
if settings.ALLOWED_ORIGINS:
    _ORIGINS.extend(
        o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**핵심:**
- `settings.ALLOWED_ORIGINS`는 `config.py`에서 이미 로드됨
- 쉼표 구분 파싱: `"https://carrot-web.railway.app,https://carrot-admin.railway.app"` → 2개 항목
- 빈 문자열이면 기존 localhost 오리진만 유지 — 로컬 개발 영향 없음

---

### Task 4: carrot-web 배포 설정

#### carrot-web/next.config.ts 수정

현재 (빈 config):
```typescript
import type { NextConfig } from "next";
const nextConfig: NextConfig = {};
export default nextConfig;
```

수정 후:
```typescript
import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  output: 'standalone',
};
export default nextConfig;
```

**`output: 'standalone'`이 필요한 이유:**
- Docker 컨테이너에서 `node server.js`로 직접 실행 가능
- `node_modules` 전체 복사 불필요 — 최소한의 필요 파일만 포함
- Railway Docker 배포의 표준 패턴

#### carrot-web/Dockerfile

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
```

**`NEXT_PUBLIC_API_URL` 주의사항:**
- `NEXT_PUBLIC_*` 변수는 빌드 타임에 번들에 인라인됨 (Next.js 스펙)
- Railway 대시보드에서 `NEXT_PUBLIC_API_URL`을 설정하면 빌드 시 `--build-arg`로 전달됨
- `ARG NEXT_PUBLIC_API_URL` + `ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL` 패턴으로 빌드 단계에서 사용 가능

#### carrot-web/.dockerignore

```
node_modules/
.next/
.env.local
.env*.local
```

---

### Task 5: carrot-admin 배포 설정

`carrot-web`과 동일한 패턴. **단, EXPOSE/PORT는 3001이 아닌 Railway가 $PORT를 주입하므로 3000 유지.**

#### carrot-admin/next.config.ts 수정

carrot-web과 동일:
```typescript
import type { NextConfig } from "next";
const nextConfig: NextConfig = {
  output: 'standalone',
};
export default nextConfig;
```

#### carrot-admin/Dockerfile

carrot-web/Dockerfile 과 완전히 동일한 내용. Railway가 각 서비스를 독립 빌드하므로 충돌 없음.

#### carrot-admin/.dockerignore

carrot-web/.dockerignore와 동일.

---

### Task 6: 검증

**Python CORS 단위 테스트 (신규):**
`carrot-api/tests/unit/test_main.py` (신규 또는 기존 파일 확인 후 추가):

```python
def test_cors_includes_env_origins(monkeypatch):
    """ALLOWED_ORIGINS 환경 변수가 CORS 오리진에 반영되는지 검증"""
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://carrot.railway.app,https://admin.railway.app")
    # settings를 재로드하여 env 변수를 반영
    from importlib import reload
    import app.core.config as cfg_module
    reload(cfg_module)
    from app.core.config import settings
    origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    assert "https://carrot.railway.app" in origins
    assert "https://admin.railway.app" in origins
    assert len(origins) == 2
```

**TypeScript 빌드 체크:**
```
npx tsc --noEmit  # carrot-web, carrot-admin 각각
```

---

### Railway 배포 절차 (코드 외 참고 사항)

1. **Railway 프로젝트 생성** → New Project → Empty Project
2. **carrot-api 서비스:**
   - GitHub repo 연결 또는 `railway up` CLI
   - Root Directory: `carrot-api`
   - 환경 변수 설정: DATABASE_URL, SUPABASE_URL, SUPABASE_KEY, JWT_SECRET, ALLOWED_ORIGINS
3. **carrot-web 서비스:**
   - Root Directory: `carrot-web`
   - 빌드 환경 변수: `NEXT_PUBLIC_API_URL=https://carrot-api.railway.app`
4. **carrot-admin 서비스:**
   - Root Directory: `carrot-admin`
   - 빌드 환경 변수: `NEXT_PUBLIC_API_URL=https://carrot-api.railway.app`
5. **ALLOWED_ORIGINS 업데이트:**
   - carrot-api 서비스의 `ALLOWED_ORIGINS`를
     `https://carrot-web.railway.app,https://carrot-admin.railway.app`로 설정
   - 재배포

---

### 현재 파일 상태 요약

| 파일 | 현재 상태 | 변경 |
|------|----------|------|
| `carrot-api/Dockerfile` | 없음 | 신규 |
| `carrot-api/.dockerignore` | 없음 | 신규 |
| `carrot-api/app/core/config.py` | 5개 필드 | ALLOWED_ORIGINS 추가 |
| `carrot-api/app/main.py` | localhost CORS만 | settings.ALLOWED_ORIGINS 반영 |
| `carrot-web/Dockerfile` | 없음 | 신규 |
| `carrot-web/.dockerignore` | 없음 | 신규 |
| `carrot-web/next.config.ts` | 빈 config | output standalone 추가 |
| `carrot-admin/Dockerfile` | 없음 | 신규 |
| `carrot-admin/.dockerignore` | 없음 | 신규 |
| `carrot-admin/next.config.ts` | 빈 config | output standalone 추가 |

### References

- [Source: epics.md#Story 6.5] — AC 전문, AR-7
- [Source: carrot-api/pyproject.toml] — uv 의존성 관리, 패키지 구조
- [Source: carrot-api/app/core/config.py] — Settings 현재 구조
- [Source: carrot-api/app/main.py] — CORS 현재 설정
- [Source: carrot-api/alembic/env.py] — Alembic 설정 (uv run alembic upgrade head 동작 확인)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Task 1: carrot-api/Dockerfile (uv sync + migrate + uvicorn), .dockerignore 생성
- Task 2: Settings에 ALLOWED_ORIGINS: str = "" 추가 (기본값 빈 문자열, 로컬 영향 없음)
- Task 3: main.py CORS에 settings.ALLOWED_ORIGINS 파싱 로직 추가 (쉼표 구분)
- Task 4: carrot-web output:standalone, Dockerfile(multi-stage ARG NEXT_PUBLIC_API_URL), .dockerignore
- Task 5: carrot-admin 동일 패턴 적용
- Task 6: CORS 파싱 단위 테스트 5개 + main.py import 테스트 — 95/95 통과, TypeScript 에러 없음

### File List

- `carrot-api/Dockerfile` (신규)
- `carrot-api/.dockerignore` (신규)
- `carrot-api/app/core/config.py` (수정: ALLOWED_ORIGINS 추가)
- `carrot-api/app/main.py` (수정: CORS env var 반영)
- `carrot-api/tests/unit/test_cors_config.py` (신규)
- `carrot-web/next.config.ts` (수정: output standalone)
- `carrot-web/Dockerfile` (신규)
- `carrot-web/.dockerignore` (신규)
- `carrot-admin/next.config.ts` (수정: output standalone)
- `carrot-admin/Dockerfile` (신규)
- `carrot-admin/.dockerignore` (신규)
