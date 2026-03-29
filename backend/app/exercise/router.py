from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from app.database import get_db
from app.models import User, ExerciseLog
from app.schemas import ExerciseLogCreate, ExerciseLogResponse, ExerciseInfo
from app.auth.utils import get_current_user
from app.exercise.calories import calculate_calories_burned, get_exercise_list

router = APIRouter(prefix="/exercise", tags=["Exercise"])


@router.get("/list", response_model=List[dict])
async def list_exercises():
    """Get all available exercises with MET values and categories."""
    return get_exercise_list()


@router.post("/log", response_model=ExerciseLogResponse)
async def log_exercise(
    data: ExerciseLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log an exercise session with auto-calculated calorie burn."""
    # Calculate calories burned using MET formula
    weight = user.weight_kg or 70.0  # Default 70kg if not set
    calories_burned = calculate_calories_burned(
        data.exercise_type, data.duration_min, weight
    )

    exercise_log = ExerciseLog(
        user_id=user.id,
        exercise_type=data.exercise_type,
        duration_min=data.duration_min,
        calories_burned=calories_burned,
        reps=data.reps,
        sets=data.sets,
    )
    db.add(exercise_log)
    await db.flush()
    await db.refresh(exercise_log)
    return ExerciseLogResponse.model_validate(exercise_log)


@router.get("/log", response_model=List[ExerciseLogResponse])
async def get_exercise_logs(
    log_date: Optional[date] = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get exercise logs for a specific date."""
    target_date = log_date or date.today()

    query = select(ExerciseLog).where(
        and_(
            ExerciseLog.user_id == user.id,
            ExerciseLog.logged_at >= datetime.combine(target_date, datetime.min.time()),
            ExerciseLog.logged_at < datetime.combine(target_date, datetime.max.time()),
        )
    ).order_by(ExerciseLog.logged_at)

    result = await db.execute(query)
    logs = result.scalars().all()
    return [ExerciseLogResponse.model_validate(log) for log in logs]


@router.delete("/log/{log_id}")
async def delete_exercise_log(
    log_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an exercise log."""
    result = await db.execute(
        select(ExerciseLog).where(ExerciseLog.id == log_id, ExerciseLog.user_id == user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    await db.delete(log)
    return {"message": "Exercise log deleted"}


@router.get("/calories-estimate")
async def estimate_calories(
    exercise_type: str = Query(...),
    duration_min: float = Query(...),
    user: User = Depends(get_current_user),
):
    """Preview calorie burn without logging."""
    weight = user.weight_kg or 70.0
    calories = calculate_calories_burned(exercise_type, duration_min, weight)
    return {
        "exercise_type": exercise_type,
        "duration_min": duration_min,
        "weight_kg": weight,
        "estimated_calories_burned": calories,
    }
