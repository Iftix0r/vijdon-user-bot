from telethon import TelegramClient, events
from src.config import settings
from src.database.models import get_db, SourceGroup, Log
from src.services.ai import analyze_message
from datetime import datetime

from src.bot.loader import bot

async def handle_new_message(event):
    # Check if chat is in monitored source groups
    chat_id = event.chat_id
    
    # Simple cache or check DB every time? For MVP check DB or memory.
    # In production, use Redis/cache.
    db = next(get_db())
    # SQLAlchemy requires standardizing chat_id format (int vs string)
    # Telethon chat_id is int.
    # Check whitelist
    allowed = db.query(SourceGroup).filter(SourceGroup.chat_id == str(chat_id), SourceGroup.active == True).first()
    
    if not allowed:
        return

    text = event.message.message
    if not text or len(text) < 10:
        return

    # Call AI
    result = await analyze_message(text)
    
    # Store Log
    try:
        log_entry = Log(
            user_id=str(event.sender_id),
            message_text=text[:200], # truncate log
            is_passenger=(result.get("type") == "PASSENGER"),
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"DB Log Error: {e}")

    # Process Result
    if result.get("type") == "PASSENGER":
        data = result.get("data", {})
        # Format the message for the driver group
        msg = (
            "🚖 **Yangi Buyurtma!**\n\n"
            f"📍 **Qayerdan:** {data.get('pickup', 'Noma\'lum')}\n"
            f"🏁 **Qayerga:** {data.get('dropoff', 'Noma\'lum')}\n"
            f"💰 **Narx:** {data.get('price', 'Kelishiladi')}\n"
            f"📞 **Aloqa:** {data.get('phone', 'Noma\'lum')}\n"
            f"📝 **Izoh:** {data.get('note', '')}\n\n"
            f"#yolovchi #{chat_id}" 
        )
        
        # Send to Target Group via BOT
        try:
             await bot.send_message(chat_id=settings.TARGET_GROUP_ID, text=msg)
        except Exception as e:
            print(f"Failed to send to target group: {e}")
            
    elif result.get("type") == "DRIVER":
        # Maybe log or execute other logic
        pass

    db.close()
