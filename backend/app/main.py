from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import httpx
from app.config import get_settings
from app.database import create_tables
from app.auth.router import router as auth_router
from app.food.router import router as food_router
from app.exercise.router import router as exercise_router
from app.dashboard.router import router as dashboard_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


async def self_ping():
    """Ping /health every 14 min to prevent Render free tier cold starts."""
    render_url = settings.RENDER_EXTERNAL_URL
    if not render_url:
        return
    await asyncio.sleep(60)  # Wait 1 min after startup
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await client.get(f"{render_url}/health", timeout=10)
                logger.debug("Self-ping OK")
            except Exception:
                pass
            await asyncio.sleep(840)  # 14 minutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create database tables + start keep-alive ping."""
    logger.info("Starting FitTracker API...")
    await create_tables()
    logger.info("Database tables created/verified.")
    ping_task = asyncio.create_task(self_ping())
    yield
    ping_task.cancel()
    logger.info("Shutting down FitTracker API.")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered fitness & nutrition tracker with CV food detection",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "https://fit.anirudhdev.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(food_router, prefix=settings.API_V1_PREFIX)
app.include_router(exercise_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
