from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


# -- Auth --
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Username must be 3-30 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least 1 number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least 1 special character")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least 1 number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least 1 special character")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[float] = None
    calorie_goal: Optional[int] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity_level: Optional[float] = None
    calorie_goal: Optional[int] = None


# -- Food --
class FoodItem(BaseModel):
    name: str
    calories: float
    protein_g: float = 0
    fat_g: float = 0
    carbs_g: float = 0
    fiber_g: float = 0
    portion: str = ""


class FoodScanResponse(BaseModel):
    foods: list[FoodItem]
    image_url: Optional[str] = None
    total_calories: float


class FoodLogCreate(BaseModel):
    meal_type: str
    food_name: str
    calories: float
    protein_g: float = 0
    fat_g: float = 0
    carbs_g: float = 0
    fiber_g: float = 0
    portion: Optional[str] = None
    image_url: Optional[str] = None
    detected_by: str = "manual"


class FoodLogResponse(BaseModel):
    id: int
    meal_type: str
    food_name: str
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: float
    portion: Optional[str]
    image_url: Optional[str]
    detected_by: str
    logged_at: datetime

    class Config:
        from_attributes = True


class TimetableCreate(BaseModel):
    day_of_week: int
    meal_type: str
    planned_food: str
    planned_calories: Optional[float] = None
    planned_time: Optional[str] = None


class TimetableResponse(BaseModel):
    id: int
    day_of_week: int
    meal_type: str
    planned_food: str
    planned_calories: Optional[float]
    planned_time: Optional[str]

    class Config:
        from_attributes = True


# -- Exercise --
class ExerciseLogCreate(BaseModel):
    exercise_type: str
    duration_min: float
    reps: Optional[int] = None
    sets: Optional[int] = None


class ExerciseLogResponse(BaseModel):
    id: int
    exercise_type: str
    duration_min: float
    calories_burned: float
    reps: Optional[int]
    sets: Optional[int]
    logged_at: datetime

    class Config:
        from_attributes = True


# -- Dashboard --
class DailySummary(BaseModel):
    date: str
    calories_consumed: float
    calories_burned: float
    net_calories: float
    calorie_target: float
    remaining_calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    meals: list[FoodLogResponse]
    exercises: list[ExerciseLogResponse]


class WeeklySummary(BaseModel):
    days: list[DailySummary]
    avg_calories_in: float
    avg_calories_burned: float
    total_workouts: int
