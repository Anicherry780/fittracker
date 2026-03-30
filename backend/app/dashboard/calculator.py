def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor equation for BMR."""
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(weight_kg: float, height_cm: float, age: int, gender: str, activity_level: float) -> float:
    """TDEE = BMR * activity multiplier."""
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    return round(bmr * activity_level)


def get_macro_targets(calorie_target: float) -> dict:
    """Balanced macro split: 30% protein, 25% fat, 45% carbs."""
    return {
        "protein_g": round(calorie_target * 0.30 / 4),
        "fat_g": round(calorie_target * 0.25 / 9),
        "carbs_g": round(calorie_target * 0.45 / 4),
    }
