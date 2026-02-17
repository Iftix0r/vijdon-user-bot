from openai import AsyncOpenAI
from src.config import settings
import json
import re

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

PROMPT = """
You are an AI assistant in a Telegram bot for identifying taxi orders in group chats.
Analyze the following Uzbek message. Determine if the sender is a PASSENGER (looking for a taxi) or a DRIVER (offering a ride).
If PASSENGER, extract:
- pickup_location (implied or explicit)
- dropoff_location (implied or explicit)
- price (if mentioned)
- contact (phone number if mentioned)
- urgency (Urgent/Normal)

Output valid JSON only:
{
  "type": "PASSENGER" | "DRIVER" | "OTHER",
  "data": {
    "pickup": "...",
    "dropoff": "...",
    "price": "...",
    "phone": "...",
    "note": "..."
  }
}
"""

async def analyze_message(text: str):
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=200
        )
        content = response.choices[0].message.content
        # Basic cleanup for json
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        return json.loads(content.strip())
    except Exception as e:
        print(f"AI Error: {e}")
        return {"type": "ERROR", "data": {}}
