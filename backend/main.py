from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.routes import router
from app.core.config import settings
from app.db.session import create_tables
from app.websockets.manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await manager.startup()

    try:
        yield
    finally:
        await manager.shutdown()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router,
    prefix="/api/v1",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
