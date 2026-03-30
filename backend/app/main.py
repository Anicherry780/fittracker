from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.auth.router import router as auth_router
from app.food.router import router as food_router
from app.exercise.router import router as exercise_router
from app.dashboard.router import router as dashboard_router

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, docs_url="/docs", redoc_url="/redoc")

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

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Mount routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(food_router, prefix=settings.API_V1_PREFIX)
app.include_router(exercise_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}
