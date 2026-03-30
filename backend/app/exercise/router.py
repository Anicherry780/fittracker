from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.database import get_db
from app.models import User, ExerciseLog
from app.schemas import ExerciseLogCreate, ExerciseLogResponse
from app.auth.utils import get_current_user
from app.exercise.calories import calculate_calories_burned, get_exercise_list

router = APIRouter(prefix="/exercise", tags=["exercise"])


@router.get("/list")
@router.get("/types")
def list_exercise_types():
    """Get all available exercise types with MET values."""
    return get_exercise_list()


@router.post("/log", response_model=ExerciseLogResponse, status_code=201)
def log_exercise(
    data: ExerciseLogCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    weight = user.weight_kg or 70.0
    calories = calculate_calories_burned(data.exercise_type, data.duration_min, weight)

    log = ExerciseLog(
        user_id=user.id,
        exercise_type=data.exercise_type,
        duration_min=data.duration_min,
        calories_burned=calories,
        reps=data.reps,
        sets=data.sets,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/log", response_model=list[ExerciseLogResponse])
def get_exercise_logs(
    target_date: date = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ExerciseLog).filter(ExerciseLog.user_id == user.id)
    if target_date:
        query = query.filter(
            ExerciseLog.logged_at >= datetime.combine(target_date, datetime.min.time()),
            ExerciseLog.logged_at < datetime.combine(target_date, datetime.max.time()),
        )
    return query.order_by(ExerciseLog.logged_at.desc()).all()


@router.delete("/log/{log_id}")
def delete_exercise_log(
    log_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = db.query(ExerciseLog).filter(ExerciseLog.id == log_id, ExerciseLog.user_id == user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Exercise log not found")
    db.delete(log)
    db.commit()
    return {"message": "Deleted"}
