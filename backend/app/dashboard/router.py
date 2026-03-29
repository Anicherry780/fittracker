from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, date, timedelta
from typing import Optional
from app.database import get_db
from app.models import User, FoodLog, ExerciseLog
from app.schemas import DailySummaryResponse, WeeklyStatsResponse
from app.auth.utils import get_current_user
from app.dashboard.calculator import calculate_tdee, calculate_calorie_balance, calculate_macro_targets

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


async def _get_daily_data(db: AsyncSession, user: User, target_date: date) -> dict:
    """Get aggregated daily food and exercise data."""
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())

    # Food totals
    food_result = await db.execute(
        select(
            func.coalesce(func.sum(FoodLog.calories), 0).label("total_cal"),
            func.coalesce(func.sum(FoodLog.protein_g), 0).label("total_protein"),
            func.coalesce(func.sum(FoodLog.fat_g), 0).label("total_fat"),
            func.coalesce(func.sum(FoodLog.carbs_g), 0).label("total_carbs"),
        ).where(
            and_(FoodLog.user_id == user.id, FoodLog.logged_at >= day_start, FoodLog.logged_at < day_end)
        )
    )
    food = food_result.one()

    # Exercise totals
    exercise_result = await db.execute(
        select(
            func.coalesce(func.sum(ExerciseLog.calories_burned), 0).label("total_burned"),
        ).where(
            and_(ExerciseLog.user_id == user.id, ExerciseLog.logged_at >= day_start, ExerciseLog.logged_at < day_end)
        )
    )
    exercise = exercise_result.one()

    # TDEE
    tdee = calculate_tdee(
        weight_kg=user.weight_kg or 70.0,
        height_cm=user.height_cm or 170.0,
        age=user.age or 25,
        gender=user.gender or "male",
        activity_level=user.activity_level or 1.55,
    )

    calorie_target = user.calorie_target or tdee
    total_calories_in = float(food.total_cal)
    total_burned = float(exercise.total_burned)
    remaining = calorie_target + total_burned - total_calories_in

    return {
        "date": target_date,
        "total_calories_in": round(total_calories_in, 1),
        "total_calories_burned": round(total_burned, 1),
        "total_protein": round(float(food.total_protein), 1),
        "total_fat": round(float(food.total_fat), 1),
        "total_carbs": round(float(food.total_carbs), 1),
        "net_calories": round(total_calories_in - tdee, 1),
        "calorie_target": round(calorie_target, 1),
        "remaining_calories": round(remaining, 1),
        "tdee": round(tdee, 1),
    }


@router.get("/today", response_model=DailySummaryResponse)
async def get_today_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's calorie and nutrition summary."""
    data = await _get_daily_data(db, user, date.today())
    return DailySummaryResponse(**data)


@router.get("/day/{target_date}", response_model=DailySummaryResponse)
async def get_day_summary(
    target_date: date,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get summary for a specific date."""
    data = await _get_daily_data(db, user, target_date)
    return DailySummaryResponse(**data)


@router.get("/week", response_model=WeeklyStatsResponse)
async def get_weekly_stats(
    start_date: Optional[date] = Query(default=None, description="Start of week (defaults to this Monday)"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get weekly nutrition and exercise stats."""
    if not start_date:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # Monday

    days = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        day_data = await _get_daily_data(db, user, day)
        days.append(DailySummaryResponse(**day_data))

    # Calculate averages
    total_days = len(days)
    avg_in = sum(d.total_calories_in for d in days) / total_days
    avg_burned = sum(d.total_calories_burned for d in days) / total_days
    avg_protein = sum(d.total_protein for d in days) / total_days

    return WeeklyStatsResponse(
        days=days,
        avg_calories_in=round(avg_in, 1),
        avg_calories_burned=round(avg_burned, 1),
        avg_protein=round(avg_protein, 1),
    )


@router.get("/macros")
async def get_macro_targets(
    goal: str = Query(default="maintain", description="Goal: lose, maintain, gain"),
    user: User = Depends(get_current_user),
):
    """Get recommended daily macro targets."""
    tdee = calculate_tdee(
        weight_kg=user.weight_kg or 70.0,
        height_cm=user.height_cm or 170.0,
        age=user.age or 25,
        gender=user.gender or "male",
        activity_level=user.activity_level or 1.55,
    )
    return calculate_macro_targets(tdee, goal)
