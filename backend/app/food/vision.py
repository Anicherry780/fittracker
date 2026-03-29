"""
AWS Bedrock Claude Vision integration for food detection.
Sends preprocessed food images to Claude and gets structured nutrition data.
"""

import boto3
import json
import base64
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_bedrock_client():
    """Create AWS Bedrock Runtime client."""
    return boto3.client(
        "bedrock-runtime",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


FOOD_ANALYSIS_PROMPT = """You are a nutrition expert. Analyze this food image and identify ALL food items visible.

For each food item, provide:
- name: The food item name (be specific, e.g., "grilled chicken breast" not just "chicken")
- calories: Estimated calories (kcal) for the visible portion
- protein_g: Estimated protein in grams
- fat_g: Estimated fat in grams
- carbs_g: Estimated carbs in grams
- portion: Estimated portion size (e.g., "1 cup", "200g", "1 medium")

Be as accurate as possible with calorie estimates based on the portion sizes visible.
If you can identify the cuisine type (Indian, Italian, etc.), factor in typical preparation methods for calorie estimation.

IMPORTANT: Respond ONLY with valid JSON in this exact format:
{
    "foods": [
        {
            "name": "food name",
            "calories": 250,
            "protein_g": 20.0,
            "fat_g": 10.0,
            "carbs_g": 30.0,
            "portion": "1 cup"
        }
    ]
}

If no food is detected in the image, respond with:
{"foods": []}
"""


async def analyze_food_image(image_bytes: bytes, content_type: str = "image/jpeg") -> dict:
    """
    Send food image to Claude Vision via AWS Bedrock and get nutrition analysis.
    Returns structured food data.
    """
    try:
        client = get_bedrock_client()

        # Encode image to base64
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        # Map content type
        media_type = content_type if content_type in ["image/jpeg", "image/png", "image/webp", "image/gif"] else "image/jpeg"

        # Bedrock Claude Messages API
        request_body = {
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
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": FOOD_ANALYSIS_PROMPT,
                        },
                    ],
                }
            ],
        }

        response = client.invoke_model(
            modelId=settings.BEDROCK_MODEL_ID,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())
        assistant_message = response_body["content"][0]["text"]

        # Parse JSON from response (handle markdown code blocks)
        json_str = assistant_message
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        result = json.loads(json_str.strip())

        # Calculate totals
        foods = result.get("foods", [])
        result["total_calories"] = sum(f.get("calories", 0) for f in foods)
        result["total_protein"] = sum(f.get("protein_g", 0) for f in foods)
        result["total_fat"] = sum(f.get("fat_g", 0) for f in foods)
        result["total_carbs"] = sum(f.get("carbs_g", 0) for f in foods)

        logger.info(f"Food analysis: detected {len(foods)} items, {result['total_calories']} kcal total")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Claude response as JSON: {e}")
        raise ValueError(f"AI returned invalid response format: {e}")
    except Exception as e:
        logger.error(f"Bedrock food analysis failed: {e}")
        raise Exception(f"Food analysis failed: {e}")
