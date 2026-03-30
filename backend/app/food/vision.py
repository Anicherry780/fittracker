import json
import base64
import boto3
from app.config import get_settings
from app.schemas import FoodItem

settings = get_settings()


def _get_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


def _parse_json_response(text: str) -> dict:
    """Extract JSON from Claude response (handles markdown code blocks)."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def estimate_food_nutrition(food_name: str, portion: str) -> FoodItem:
    """Estimate nutrition for a food item using AI (text-only, no image)."""
    client = _get_bedrock_client()

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Estimate the nutritional content of: {food_name}, portion: {portion}.\n"
                    "Consider all cuisines (Indian, Asian, Western, etc.).\n"
                    "Respond ONLY with valid JSON in this exact format:\n"
                    '{"name": "food name", "calories": 250, '
                    '"protein_g": 10, "fat_g": 8, "carbs_g": 30, '
                    '"fiber_g": 3, "portion": "the portion"}\n'
                    "Be accurate with estimates based on the specified portion size."
                ),
            }
        ],
    })

    response = client.invoke_model(
        modelId=settings.BEDROCK_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    result = json.loads(response["body"].read())
    text = result["content"][0]["text"]
    parsed = _parse_json_response(text)
    return FoodItem(**parsed)


def analyze_food_image(image_bytes: bytes) -> list[FoodItem]:
    """Send food image to AWS Bedrock Claude Vision for analysis."""
    client = _get_bedrock_client()

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Analyze this food image. Identify ALL food items visible. "
                            "Consider foods from ALL cuisines including Indian (samosa, biryani, dal, roti, paneer, etc.), "
                            "Asian, Mediterranean, Latin American, and Western dishes. "
                            "For each item, estimate the portion size and nutritional content. "
                            "Respond ONLY with valid JSON in this exact format:\n"
                            '{"foods": [{"name": "food name", "calories": 250, '
                            '"protein_g": 10, "fat_g": 8, "carbs_g": 30, '
                            '"fiber_g": 3, "portion": "1 cup / 200g"}]}\n'
                            "Be accurate with calorie estimates and food identification. "
                            "Include all visible items including sides, drinks, and condiments."
                        ),
                    },
                ],
            }
        ],
    })

    response = client.invoke_model(
        modelId=settings.BEDROCK_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    result = json.loads(response["body"].read())
    text = result["content"][0]["text"]

    parsed = _parse_json_response(text)
    return [FoodItem(**item) for item in parsed["foods"]]
