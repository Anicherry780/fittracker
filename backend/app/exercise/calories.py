"""
MET-based calorie burn calculator.
MET (Metabolic Equivalent of Task) values from the Compendium of Physical Activities.
Formula: Calories = MET × weight_kg × duration_hours
"""

# Comprehensive MET values database
MET_VALUES = {
    # Strength Training
    "push_up": 8.0,
    "pull_up": 8.0,
    "squat": 5.0,
    "deadlift": 6.0,
    "bench_press": 5.0,
    "shoulder_press": 5.0,
    "bicep_curl": 4.0,
    "tricep_dip": 5.0,
    "lunges": 5.0,
    "plank": 3.8,
    "burpees": 8.0,
    "sit_up": 4.0,
    "crunches": 3.8,
    "leg_press": 5.0,
    "lat_pulldown": 5.0,
    "rows": 5.0,
    "chest_fly": 4.5,
    "lateral_raise": 4.0,
    "weight_training_general": 5.0,
    "weight_training_vigorous": 6.0,
    "resistance_bands": 4.0,
    "kettlebell": 6.0,

    # Cardio
    "running": 9.8,
    "running_slow": 7.0,
    "running_fast": 12.0,
    "jogging": 7.0,
    "walking": 3.5,
    "walking_brisk": 4.5,
    "cycling": 7.5,
    "cycling_stationary": 7.0,
    "cycling_vigorous": 10.0,
    "swimming": 6.0,
    "swimming_vigorous": 9.8,
    "jump_rope": 10.0,
    "jumping_jacks": 8.0,
    "stair_climbing": 8.0,
    "elliptical": 5.0,
    "rowing_machine": 7.0,
    "treadmill": 8.0,
    "hiit": 8.0,

    # Sports
    "basketball": 6.5,
    "soccer": 7.0,
    "tennis": 7.3,
    "badminton": 5.5,
    "volleyball": 4.0,
    "cricket": 5.0,
    "table_tennis": 4.0,
    "boxing": 7.8,
    "kickboxing": 7.0,
    "martial_arts": 10.3,

    # Flexibility & Balance
    "yoga": 3.0,
    "pilates": 3.8,
    "stretching": 2.5,
    "tai_chi": 3.0,

    # Daily Activities
    "dancing": 5.0,
    "hiking": 6.0,
    "climbing": 8.0,
    "gardening": 3.5,
    "housework": 3.0,
}

# Exercise categories
EXERCISE_CATEGORIES = {
    "Strength": [
        "push_up", "pull_up", "squat", "deadlift", "bench_press",
        "shoulder_press", "bicep_curl", "tricep_dip", "lunges", "plank",
        "burpees", "sit_up", "crunches", "leg_press", "lat_pulldown",
        "rows", "chest_fly", "lateral_raise", "weight_training_general",
        "weight_training_vigorous", "resistance_bands", "kettlebell",
    ],
    "Cardio": [
        "running", "running_slow", "running_fast", "jogging", "walking",
        "walking_brisk", "cycling", "cycling_stationary", "cycling_vigorous",
        "swimming", "swimming_vigorous", "jump_rope", "jumping_jacks",
        "stair_climbing", "elliptical", "rowing_machine", "treadmill", "hiit",
    ],
    "Sports": [
        "basketball", "soccer", "tennis", "badminton", "volleyball",
        "cricket", "table_tennis", "boxing", "kickboxing", "martial_arts",
    ],
    "Flexibility": [
        "yoga", "pilates", "stretching", "tai_chi",
    ],
    "Other": [
        "dancing", "hiking", "climbing", "gardening", "housework",
    ],
}


def calculate_calories_burned(exercise_type: str, duration_min: float, weight_kg: float = 70.0) -> float:
    """
    Calculate calories burned using MET formula.
    Calories = MET × weight_kg × (duration_min / 60)
    """
    exercise_key = exercise_type.lower().replace(" ", "_").replace("-", "_")
    met = MET_VALUES.get(exercise_key, 5.0)  # Default MET of 5.0 for unknown exercises
    duration_hours = duration_min / 60.0
    return round(met * weight_kg * duration_hours, 1)


def get_exercise_list() -> list:
    """Return all available exercises with MET values and categories."""
    exercises = []
    for category, exercise_keys in EXERCISE_CATEGORIES.items():
        for key in exercise_keys:
            exercises.append({
                "name": key,
                "display_name": key.replace("_", " ").title(),
                "met_value": MET_VALUES[key],
                "category": category,
            })
    return exercises
