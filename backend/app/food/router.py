from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.database import get_db
from app.models import User, FoodLog, FoodTimetable, MealType, DetectionMethod
from app.schemas import (
    FoodScanResponse, FoodEstimateRequest, FoodItem,
    FoodLogCreate, FoodLogResponse,
    TimetableCreate, TimetableResponse,
)
from app.auth.utils import get_current_user
from app.food.cv_processing import preprocess_food_image
from app.food.vision import analyze_food_image, estimate_food_nutrition
from app.storage.r2 import upload_image

router = APIRouter(prefix="/food", tags=["food"])


@router.post("/analyze", response_model=FoodScanResponse)
@router.post("/scan", response_model=FoodScanResponse)
async def scan_food(
    file: UploadFile = File(...),
    meal_type: str = Query("snack"),
    auto_log: bool = Query(False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a food image → CV preprocessing → AI analysis → nutrition data."""
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 10MB")

    # CV preprocessing
    processed = preprocess_food_image(contents)

    # Upload to R2
    image_url = None
    try:
        image_url = upload_image(processed, file.content_type or "image/jpeg")
    except Exception:
        pass  # R2 upload is optional — don't block the scan

    # AI analysis via Bedrock
    try:
        foods = analyze_food_image(processed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    total_calories = sum(f.calories for f in foods)
    total_protein = sum(f.protein_g for f in foods)
    total_fat = sum(f.fat_g for f in foods)
    total_carbs = sum(f.carbs_g for f in foods)

    # Auto-log if requested
    if auto_log:
        for food in foods:
            log = FoodLog(
                user_id=user.id,
                meal_type=meal_type,
                food_name=food.name,
                calories=food.calories,
                protein_g=food.protein_g,
                fat_g=food.fat_g,
                carbs_g=food.carbs_g,
                fiber_g=food.fiber_g,
                portion=food.portion,
                image_url=image_url,
                detected_by=DetectionMethod.ai,
            )
            db.add(log)
        db.commit()

    return FoodScanResponse(
        foods=foods, image_url=image_url,
        total_calories=total_calories, total_protein=total_protein,
        total_fat=total_fat, total_carbs=total_carbs,
    )


@router.post("/estimate", response_model=FoodItem)
async def estimate_nutrition(
    data: FoodEstimateRequest,
    user: User = Depends(get_current_user),
):
    """Estimate nutrition for a food item by name and portion (text-only AI)."""
    try:
        return estimate_food_nutrition(data.food_name, data.portion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Estimation failed: {str(e)}")


@router.post("/log", response_model=FoodLogResponse, status_code=201)
def create_food_log(
    data: FoodLogCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = FoodLog(user_id=user.id, **data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/log", response_model=list[FoodLogResponse])
def get_food_logs(
    target_date: date = Query(None),
    log_date: date = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(FoodLog).filter(FoodLog.user_id == user.id)
    filter_date = target_date or log_date
    if filter_date:
        query = query.filter(
            FoodLog.logged_at >= datetime.combine(filter_date, datetime.min.time()),
            FoodLog.logged_at < datetime.combine(filter_date, datetime.max.time()),
        )
    return query.order_by(FoodLog.logged_at.desc()).all()


@router.delete("/log/{log_id}")
def delete_food_log(
    log_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = db.query(FoodLog).filter(FoodLog.id == log_id, FoodLog.user_id == user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    db.delete(log)
    db.commit()
    return {"message": "Deleted"}


# -- Timetable --
@router.post("/timetable", response_model=TimetableResponse, status_code=201)
def create_timetable_entry(
    data: TimetableCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = FoodTimetable(user_id=user.id, **data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/timetable", response_model=list[TimetableResponse])
def get_timetable(
    day: int = Query(None, ge=0, le=6),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(FoodTimetable).filter(FoodTimetable.user_id == user.id)
    if day is not None:
        query = query.filter(FoodTimetable.day_of_week == day)
    return query.order_by(FoodTimetable.day_of_week, FoodTimetable.planned_time).all()


@router.delete("/timetable/{entry_id}")
def delete_timetable_entry(
    entry_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = db.query(FoodTimetable).filter(
        FoodTimetable.id == entry_id, FoodTimetable.user_id == user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Timetable entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Deleted"}
