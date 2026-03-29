"""
TDEE (Total Daily Energy Expenditure) and calorie balance calculator.
Uses Harris-Benedict equation for BMR estimation.
"""


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate using Harris-Benedict equation.
    Returns BMR in kcal/day.
    """
    if gender == "male":
        return 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        return 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)


def calculate_tdee(
    weight_kg: float = 70.0,
    height_cm: float = 170.0,
    age: int = 25,
    gender: str = "male",
    activity_level: float = 1.55,
) -> float:
    """
    Calculate Total Daily Energy Expenditure.

    Activity levels:
    1.2  = Sedentary (little/no exercise)
    1.375 = Lightly active (1-3 days/week)
    1.55  = Moderately active (3-5 days/week)
    1.725 = Very active (6-7 days/week)
    1.9   = Extra active (very hard exercise, physical job)
    """
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    return round(bmr * activity_level, 1)


def calculate_calorie_balance(
    tdee: float,
    calories_consumed: float,
    calories_burned_exercise: float,
) -> dict:
    """
    Calculate daily calorie balance.

    Total budget = TDEE + exercise_burn
    Net = consumed - TDEE (negative = deficit = weight loss)
    Remaining = TDEE + exercise_burn - consumed
    """
    total_budget = tdee + calories_burned_exercise
    remaining = total_budget - calories_consumed
    net = calories_consumed - tdee

    return {
        "tdee": round(tdee, 1),
        "calories_consumed": round(calories_consumed, 1),
        "calories_burned_exercise": round(calories_burned_exercise, 1),
        "total_budget": round(total_budget, 1),
        "remaining_calories": round(remaining, 1),
        "net_calories": round(net, 1),
        "status": "deficit" if net < 0 else "surplus" if net > 0 else "maintenance",
    }


def calculate_macro_targets(tdee: float, goal: str = "maintain") -> dict:
    """
    Calculate recommended macro targets based on TDEE and goal.

    Goals: 'lose', 'maintain', 'gain'
    """
    if goal == "lose":
        target_calories = tdee - 500  # 500 kcal deficit
        protein_pct, fat_pct, carbs_pct = 0.35, 0.30, 0.35
    elif goal == "gain":
        target_calories = tdee + 300  # 300 kcal surplus
        protein_pct, fat_pct, carbs_pct = 0.30, 0.25, 0.45
    else:  # maintain
        target_calories = tdee
        protein_pct, fat_pct, carbs_pct = 0.30, 0.30, 0.40

    return {
        "target_calories": round(target_calories, 1),
        "protein_g": round((target_calories * protein_pct) / 4, 1),   # 4 cal/g
        "fat_g": round((target_calories * fat_pct) / 9, 1),           # 9 cal/g
        "carbs_g": round((target_calories * carbs_pct) / 4, 1),       # 4 cal/g
    }
