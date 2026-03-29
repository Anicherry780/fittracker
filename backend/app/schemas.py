from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
import re


# ─── Auth Schemas ───

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be 3-50 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[float] = 1.55
    calorie_target: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[float] = None
    calorie_target: Optional[int] = None


# ─── Food Schemas ───

class FoodItem(BaseModel):
    name: str
    calories: float
    protein_g: float = 0
    fat_g: float = 0
    carbs_g: float = 0
    portion: Optional[str] = None


class FoodAnalysisResponse(BaseModel):
    foods: List[FoodItem]
    image_url: Optional[str] = None
    total_calories: float
    total_protein: float
    total_fat: float
    total_carbs: float


class FoodLogCreate(BaseModel):
    meal_type: str  # breakfast, lunch, dinner, snack
    food_name: str
    calories: float
    protein_g: float = 0
    fat_g: float = 0
    carbs_g: float = 0
    portion: Optional[str] = None
    image_url: Optional[str] = None
    detected_by: str = "manual"


class FoodLogResponse(BaseModel):
    id: UUID
    meal_type: str
    food_name: str
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    portion: Optional[str]
    image_url: Optional[str]
    detected_by: str
    logged_at: datetime

    model_config = {"from_attributes": True}


# ─── Food Timetable ───

class TimetableCreate(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    meal_type: str
    planned_food: str
    planned_calories: Optional[float] = None
    planned_time: Optional[str] = None


class TimetableResponse(BaseModel):
    id: UUID
    day_of_week: int
    meal_type: str
    planned_food: str
    planned_calories: Optional[float]
    planned_time: Optional[str]

    model_config = {"from_attributes": True}


# ─── Exercise Schemas ───

class ExerciseLogCreate(BaseModel):
    exercise_type: str
    duration_min: float
    reps: Optional[int] = None
    sets: Optional[int] = None


class ExerciseLogResponse(BaseModel):
    id: UUID
    exercise_type: str
    duration_min: float
    calories_burned: float
    reps: Optional[int]
    sets: Optional[int]
    logged_at: datetime

    model_config = {"from_attributes": True}


class ExerciseInfo(BaseModel):
    name: str
    met_value: float
    category: str


# ─── Dashboard Schemas ───

class DailySummaryResponse(BaseModel):
    date: date
    total_calories_in: float
    total_calories_burned: float
    total_protein: float
    total_fat: float
    total_carbs: float
    net_calories: float
    calorie_target: float
    remaining_calories: float
    tdee: float


class WeeklyStatsResponse(BaseModel):
    days: List[DailySummaryResponse]
    avg_calories_in: float
    avg_calories_burned: float
    avg_protein: float


# Resolve forward reference
TokenResponse.model_rebuild()
