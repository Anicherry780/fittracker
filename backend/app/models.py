from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class DetectionMethod(str, enum.Enum):
    ai = "ai"
    manual = "manual"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(SAEnum(Gender), nullable=True)
    activity_level = Column(Float, default=1.55)
    calorie_goal = Column(Integer, nullable=True)

    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    exercise_logs = relationship("ExerciseLog", back_populates="user", cascade="all, delete-orphan")
    food_timetable = relationship("FoodTimetable", back_populates="user", cascade="all, delete-orphan")


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_type = Column(SAEnum(MealType), nullable=False)
    food_name = Column(String(255), nullable=False)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, default=0)
    fat_g = Column(Float, default=0)
    carbs_g = Column(Float, default=0)
    fiber_g = Column(Float, default=0)
    portion = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    detected_by = Column(SAEnum(DetectionMethod), default=DetectionMethod.manual)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="food_logs")


class FoodTimetable(Base):
    __tablename__ = "food_timetable"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    meal_type = Column(SAEnum(MealType), nullable=False)
    planned_food = Column(String(255), nullable=False)
    planned_calories = Column(Float, nullable=True)
    planned_time = Column(String(10), nullable=True)

    user = relationship("User", back_populates="food_timetable")


class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_type = Column(String(100), nullable=False)
    duration_min = Column(Float, nullable=False)
    calories_burned = Column(Float, nullable=False)
    reps = Column(Integer, nullable=True)
    sets = Column(Integer, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="exercise_logs")
