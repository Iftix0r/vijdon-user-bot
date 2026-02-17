# Vijdon User Bot
ass
Pythonda yozilgan zamonaviy Telegram Userbot + Bot.
Ushbu loyiha Telegram guruhlardagi xasssbarlarni kuzatib, hassydovchi va yo'lovchilarni aniqlaydi va buyurtmalarni alohida guruhga yuboradi

## Xususiyatlari
- **Userbot (Telethon)**: Guruhdagi xabarlarni o'qiydi.
- **AI (OpenAI)**: Xabarlarni tahlil qiladi (Haydovchi vs Yo'lovchi).
- **Bot (Aiogram)**: Buyurtmalarni yetkazib beradi va admin panel vazifasini bajaradi.
- **Admin Panel (Web)**: Statistikalar va guruhlarni boshqarish uchun veb interfeys.

## O'rnatish

1. Talablarni o'rnatish:
   ```bash
   pip install -r requirements.txt
   ```

2. Sozlamalar (.env faylini yarating):
   ```bash
   cp .env.example .env
   nano .env
   ```
   Telegram API ID va Hash olish uchun: https://my.telegram.org
   Bot Token olish uchun: @BotFather

3. Ishga tushirish:
   ```bash
   chmod +x run.sh
   ./run.sh
   # Yoki
   python3 src/main.py
   ```

## Admin Paneli
Bot ishga tushgandan so'ng, brauzerda `http://localhost:8000` manziliga kiring.

## Bot Komandalari
- `/start` - Botni ishga tushirish
- `/admin` - Boshqaruv tugmalari (Guruh qo'shish/o'chirish)
- `/stats` - Statistika
- `/add <chat_id> <nomi>` - Guruhni kuzatuvga qo'shish

## Texnologiyalar
- Python 3.10+
- Aiogram 3.x
- Telethon
- OpenAI API
- FastAPI (Web Panel)
- SQLAlchemy (Database)
