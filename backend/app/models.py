import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Date,
    ForeignKey, Enum as SAEnum, Text, Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class DetectionMethod(str, enum.Enum):
    AI = "ai"
    MANUAL = "manual"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Profile info for TDEE calculation
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(SAEnum(Gender), nullable=True)
    activity_level = Column(Float, default=1.55)  # Moderate activity multiplier
    calorie_target = Column(Integer, nullable=True)  # Manual override

    # Password reset
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Relationships
    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    exercise_logs = relationship("ExerciseLog", back_populates="user", cascade="all, delete-orphan")
    food_timetable = relationship("FoodTimetable", back_populates="user", cascade="all, delete-orphan")
    daily_summaries = relationship("DailySummary", back_populates="user", cascade="all, delete-orphan")


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    meal_type = Column(SAEnum(MealType), nullable=False)
    food_name = Column(String(255), nullable=False)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    portion = Column(String(100), nullable=True)  # e.g., "1 cup", "200g"
    image_url = Column(Text, nullable=True)
    detected_by = Column(SAEnum(DetectionMethod), default=DetectionMethod.MANUAL)
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="food_logs")


class FoodTimetable(Base):
    __tablename__ = "food_timetable"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    meal_type = Column(SAEnum(MealType), nullable=False)
    planned_food = Column(String(255), nullable=False)
    planned_calories = Column(Float, nullable=True)
    planned_time = Column(String(10), nullable=True)  # "08:00", "13:00"

    user = relationship("User", back_populates="food_timetable")


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exercise_type = Column(String(100), nullable=False)
    duration_min = Column(Float, nullable=False)
    calories_burned = Column(Float, nullable=False)
    reps = Column(Integer, nullable=True)
    sets = Column(Integer, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="exercise_logs")


class DailySummary(Base):
    __tablename__ = "daily_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    total_calories_in = Column(Float, default=0)
    total_calories_burned = Column(Float, default=0)
    total_protein = Column(Float, default=0)
    total_fat = Column(Float, default=0)
    total_carbs = Column(Float, default=0)
    net_calories = Column(Float, default=0)
    calorie_target = Column(Float, default=2000)

    user = relationship("User", back_populates="daily_summaries")
