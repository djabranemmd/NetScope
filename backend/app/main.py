
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.interfaces import router as interfaces_router
from app.api.capture import router as capture_router
from app.api.analytics import router as analytics_router


app = FastAPI(
    title="NetScope API",
    description=(
        "Intelligent Network Traffic Analysis "
        "and Anomaly Detection Platform."
    ),
    version="0.3.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    interfaces_router,
    prefix="/api/v1",
)

app.include_router(
    capture_router,
    prefix="/api/v1",
)

app.include_router(
    analytics_router,
    prefix="/api/v1",
)


@app.get("/")
async def root():
    return {
        "name": "NetScope",
        "description": "Network Traffic Analysis Platform",
        "version": "0.3.0",
        "documentation": "/docs",
    }
