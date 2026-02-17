from openai import AsyncOpenAI
from src.config import settings
import json
import re

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

PROMPT = """
Siz Telegram guruhlaridagi taksi buyurtmalarini aniqlaydigan AI yordamchisiz.

Quyidagi O'zbek tilidagi xabarni tahlil qiling va quyidagilarni aniqlang:
1. Xabar turi: PASSENGER (yo'lovchi, taksi izlayapti) yoki DRIVER (haydovchi, yo'lovchi izlayapti) yoki OTHER (boshqa)
2. Agar PASSENGER bo'lsa, quyidagilarni ajratib oling:
   - Qayerdan (pickup): joy nomi, ko'cha, bino
   - Qayerga (dropoff): manzil
   - Narx (price): agar aytilgan bo'lsa
   - Telefon (phone): agar aytilgan bo'lsa
   - Qo'shimcha (note): boshqa ma'lumotlar

Faqat JSON formatida javob bering:
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

Misollar:
- "Chorsu dan Yunusobodga kerak" -> PASSENGER, pickup: Chorsu, dropoff: Yunusobod
- "Sergeli dan shaharga boraman, 3 joy bor" -> DRIVER
- "Salom" -> OTHER
"""

async def analyze_message(text: str):
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
            max_tokens=250,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        return json.loads(content.strip())
    except Exception as e:
        print(f"AI Error: {e}")
        return {"type": "ERROR", "data": {}}
