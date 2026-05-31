from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_router
from app.core.config import settings
from app.shared.exceptions import AppException, app_exception_handler

app = FastAPI(title="carrot API", version="1.0.0", description="carrot 중고거래 플랫폼 API")

# CORS 설정 (NFR-4: 3개 오리진 허용 + 환경변수 추가 오리진)
_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
]
if settings.ALLOWED_ORIGINS:
    _ORIGINS.extend(
        o.strip()
        for o in settings.ALLOWED_ORIGINS.split(",")
        if o.strip() and o.strip() != "*"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
