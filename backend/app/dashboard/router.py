from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta

from app.database import get_db
from app.models import User, FoodLog, ExerciseLog
from app.schemas import DailySummary, WeeklySummary, FoodLogResponse, ExerciseLogResponse
from app.auth.utils import get_current_user
from app.dashboard.calculator import calculate_tdee

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _get_daily_summary(user: User, target_date: date, db: Session) -> DailySummary:
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())

    meals = db.query(FoodLog).filter(
        FoodLog.user_id == user.id,
        FoodLog.logged_at >= day_start,
        FoodLog.logged_at <= day_end,
    ).order_by(FoodLog.logged_at).all()

    exercises = db.query(ExerciseLog).filter(
        ExerciseLog.user_id == user.id,
        ExerciseLog.logged_at >= day_start,
        ExerciseLog.logged_at <= day_end,
    ).order_by(ExerciseLog.logged_at).all()

    calories_consumed = round(sum(m.calories for m in meals), 1)
    calories_burned = round(sum(e.calories_burned for e in exercises), 1)

    # Calculate calorie target
    if user.calorie_goal:
        calorie_target = user.calorie_goal
    elif user.weight_kg and user.height_cm and user.age and user.gender:
        calorie_target = calculate_tdee(
            user.weight_kg, user.height_cm, user.age,
            user.gender, user.activity_level or 1.55,
        )
    else:
        calorie_target = 2000

    remaining = round(calorie_target + calories_burned - calories_consumed, 1)

    return DailySummary(
        date=target_date.isoformat(),
        calories_consumed=calories_consumed,
        calories_burned=calories_burned,
        net_calories=round(calories_consumed - calories_burned, 1),
        calorie_target=calorie_target,
        remaining_calories=remaining,
        protein_g=round(sum(m.protein_g for m in meals), 1),
        fat_g=round(sum(m.fat_g for m in meals), 1),
        carbs_g=round(sum(m.carbs_g for m in meals), 1),
        meals=[FoodLogResponse.model_validate(m) for m in meals],
        exercises=[ExerciseLogResponse.model_validate(e) for e in exercises],
    )


@router.get("/today")
@router.get("/daily")
def get_daily_summary(
    target_date: date = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not target_date:
        target_date = date.today()
    return _get_daily_summary(user, target_date, db)


@router.get("/weekly", response_model=WeeklySummary)
def get_weekly_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        days.append(_get_daily_summary(user, day, db))

    total_in = sum(d.calories_consumed for d in days)
    total_burned = sum(d.calories_burned for d in days)
    total_workouts = sum(len(d.exercises) for d in days)

    return WeeklySummary(
        days=days,
        avg_calories_in=round(total_in / 7, 1),
        avg_calories_burned=round(total_burned / 7, 1),
        total_workouts=total_workouts,
    )
