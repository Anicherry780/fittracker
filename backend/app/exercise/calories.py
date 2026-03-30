MET_VALUES = {
    "push_up": 8.0,
    "pull_up": 8.0,
    "squat": 5.0,
    "sit_up": 3.8,
    "plank": 3.8,
    "burpee": 10.0,
    "jumping_jack": 8.0,
    "lunge": 5.0,
    "deadlift": 6.0,
    "bench_press": 5.0,
    "shoulder_press": 5.0,
    "bicep_curl": 3.5,
    "tricep_dip": 5.0,
    "leg_press": 5.0,
    "calf_raise": 3.0,
    "lat_pulldown": 5.0,
    "rowing_machine": 7.0,
    "running": 9.8,
    "jogging": 7.0,
    "walking": 3.5,
    "cycling": 7.5,
    "swimming": 8.0,
    "jump_rope": 12.3,
    "elliptical": 5.0,
    "stair_climbing": 9.0,
    "yoga": 3.0,
    "pilates": 3.0,
    "boxing": 7.8,
    "kickboxing": 10.0,
    "dancing": 5.5,
    "hiking": 6.0,
    "rock_climbing": 8.0,
    "tennis": 7.3,
    "basketball": 6.5,
    "soccer": 7.0,
    "volleyball": 4.0,
    "badminton": 5.5,
    "table_tennis": 4.0,
    "cricket": 5.0,
    "martial_arts": 10.3,
    "stretching": 2.3,
    "foam_rolling": 2.0,
    "battle_ropes": 10.3,
    "kettlebell_swing": 9.8,
    "mountain_climber": 8.0,
    "wall_sit": 3.5,
    "high_knees": 8.0,
    "box_jump": 8.0,
    "russian_twist": 4.0,
    "leg_raise": 3.5,
}


def calculate_calories_burned(exercise_type: str, duration_min: float, weight_kg: float) -> float:
    """Calculate calories burned using MET formula: MET * weight_kg * duration_hours."""
    met = MET_VALUES.get(exercise_type.lower().replace(" ", "_").replace("-", "_"), 5.0)
    duration_hours = duration_min / 60
    return round(met * weight_kg * duration_hours, 1)


def get_exercise_list() -> list[dict]:
    """Return all available exercises with their MET values."""
    return [
        {"name": name.replace("_", " ").title(), "key": name, "met": met}
        for name, met in sorted(MET_VALUES.items())
    ]
