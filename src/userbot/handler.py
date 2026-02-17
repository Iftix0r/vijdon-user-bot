from telethon import TelegramClient, events
from src.config import settings
from src.database.models import get_db, SourceGroup, Log
from src.services.ai import analyze_message
from datetime import datetime

from src.bot.loader import bot

async def handle_new_message(event):
    chat_id = event.chat_id
    
    db = next(get_db())
    allowed = db.query(SourceGroup).filter(SourceGroup.chat_id == str(chat_id), SourceGroup.active == True).first()
    
    if not allowed:
        db.close()
        return

    text = event.message.message
    if not text or len(text) < 10:
        db.close()
        return

    # Call AI
    result = await analyze_message(text)
    
    # Store Log
    try:
        log_entry = Log(
            user_id=str(event.sender_id),
            message_text=text[:200],
            is_passenger=(result.get("type") == "PASSENGER"),
            timestamp=datetime.utcnow(),
            source_chat_id=str(chat_id)
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"DB Log Error: {e}")

    # Process Result
    if result.get("type") == "PASSENGER":
        data = result.get("data", {})
        
        # Get sender info
        sender = await event.get_sender()
        sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
        sender_username = f"@{sender.username}" if sender.username else ""
        
        msg = (
            "🚖 **Yangi Buyurtma!**\n\n"
            f"📍 **Qayerdan:** {data.get('pickup', 'Nomalum')}\n"
            f"🏁 **Qayerga:** {data.get('dropoff', 'Nomalum')}\n"
            f"💰 **Narx:** {data.get('price', 'Kelishiladi')}\n"
            f"📞 **Aloqa:** {data.get('phone', sender_username or 'Nomalum')}\n"
        )
        
        if data.get('note'):
            msg += f"📝 **Izoh:** {data.get('note')}\n"
        
        msg += f"\n👤 **Mijoz:** {sender_name} {sender_username}\n"
        msg += f"💬 **Guruh:** {allowed.name or chat_id}\n\n"
        msg += f"#buyurtma #{chat_id}"
        
        try:
            await bot.send_message(chat_id=settings.TARGET_GROUP_ID, text=msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to send to target group: {e}")

    db.close()
