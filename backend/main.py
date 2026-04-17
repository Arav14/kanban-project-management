from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import create_tables
from app.websockets.manager import manager
from app.api.routes.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    await manager.startup()
    yield
    # Shutdown ( cleanup if needed )

app = FastAPI(
    title = settings.APP_NAME,
    lifespan = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(router, prefix = "/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}