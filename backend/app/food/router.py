from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from app.database import get_db
from app.models import User, FoodLog, FoodTimetable, MealType, DetectionMethod
from app.schemas import (
    FoodLogCreate, FoodLogResponse, FoodAnalysisResponse,
    TimetableCreate, TimetableResponse
)
from app.auth.utils import get_current_user
from app.food.cv_processing import preprocess_food_image
from app.food.vision import analyze_food_image
from app.storage.r2 import upload_image
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/food", tags=["Food"])


@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """
    Upload a food image for AI-powered analysis.
    Pipeline: CV preprocessing → R2 upload → Claude Vision → nutrition JSON
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read image
    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Image must be under 10MB")

    # CV preprocessing pipeline
    try:
        processed_bytes, quality = preprocess_food_image(image_bytes)
        logger.info(f"Image preprocessed: {quality}")
    except Exception as e:
        logger.warning(f"Preprocessing failed, using original: {e}")
        processed_bytes = image_bytes

    # Upload to R2
    try:
        image_url = await upload_image(processed_bytes, file.content_type or "image/jpeg")
    except Exception as e:
        logger.warning(f"R2 upload failed, continuing without: {e}")
        image_url = None

    # Analyze with Claude Vision
    try:
        result = await analyze_food_image(processed_bytes, file.content_type or "image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Food analysis failed: {e}")

    result["image_url"] = image_url
    return FoodAnalysisResponse(**result)


@router.post("/log", response_model=FoodLogResponse)
async def create_food_log(
    data: FoodLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log a food item (manual or from AI analysis)."""
    food_log = FoodLog(
        user_id=user.id,
        meal_type=MealType(data.meal_type),
        food_name=data.food_name,
        calories=data.calories,
        protein_g=data.protein_g,
        fat_g=data.fat_g,
        carbs_g=data.carbs_g,
        portion=data.portion,
        image_url=data.image_url,
        detected_by=DetectionMethod(data.detected_by),
    )
    db.add(food_log)
    await db.flush()
    await db.refresh(food_log)
    return FoodLogResponse.model_validate(food_log)


@router.get("/log", response_model=List[FoodLogResponse])
async def get_food_logs(
    log_date: Optional[date] = Query(default=None, description="Date to filter (YYYY-MM-DD)"),
    meal_type: Optional[str] = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get food logs for a specific date."""
    target_date = log_date or date.today()

    query = select(FoodLog).where(
        and_(
            FoodLog.user_id == user.id,
            FoodLog.logged_at >= datetime.combine(target_date, datetime.min.time()),
            FoodLog.logged_at < datetime.combine(target_date, datetime.max.time()),
        )
    )
    if meal_type:
        query = query.where(FoodLog.meal_type == MealType(meal_type))

    query = query.order_by(FoodLog.logged_at)
    result = await db.execute(query)
    logs = result.scalars().all()
    return [FoodLogResponse.model_validate(log) for log in logs]


@router.delete("/log/{log_id}")
async def delete_food_log(
    log_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a food log entry."""
    result = await db.execute(
        select(FoodLog).where(FoodLog.id == log_id, FoodLog.user_id == user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    await db.delete(log)
    return {"message": "Food log deleted"}


# ─── Timetable ───

@router.post("/timetable", response_model=TimetableResponse)
async def create_timetable_entry(
    data: TimetableCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a planned meal to the timetable."""
    entry = FoodTimetable(
        user_id=user.id,
        day_of_week=data.day_of_week,
        meal_type=MealType(data.meal_type),
        planned_food=data.planned_food,
        planned_calories=data.planned_calories,
        planned_time=data.planned_time,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return TimetableResponse.model_validate(entry)


@router.get("/timetable", response_model=List[TimetableResponse])
async def get_timetable(
    day: Optional[int] = Query(default=None, description="Day of week (0=Mon, 6=Sun)"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get meal timetable entries."""
    query = select(FoodTimetable).where(FoodTimetable.user_id == user.id)
    if day is not None:
        query = query.where(FoodTimetable.day_of_week == day)
    query = query.order_by(FoodTimetable.day_of_week, FoodTimetable.planned_time)
    result = await db.execute(query)
    entries = result.scalars().all()
    return [TimetableResponse.model_validate(e) for e in entries]


@router.delete("/timetable/{entry_id}")
async def delete_timetable_entry(
    entry_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a timetable entry."""
    result = await db.execute(
        select(FoodTimetable).where(FoodTimetable.id == entry_id, FoodTimetable.user_id == user.id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    await db.delete(entry)
    return {"message": "Timetable entry deleted"}
