from aiogram import BaseMiddleware
from aiogram.types import Update, ErrorEvent
from src.config import settings
import traceback

class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Update, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            error_text = f"⚠️ **Bot Xatosi:**\n\n"
            error_text += f"Xato: {str(e)[:300]}\n\n"
            error_text += f"Traceback:\n```\n{traceback.format_exc()[:500]}\n```"
            
            try:
                from src.bot.loader import bot
                await bot.send_message(chat_id=settings.ADMIN_ID, text=error_text, parse_mode="Markdown")
            except:
                pass
            
            raise

async def error_handler(event: ErrorEvent):
    error_text = f"⚠️ **Bot Xatosi:**\n\n"
    error_text += f"Xato: {str(event.exception)[:300]}\n\n"
    error_text += f"Update: {event.update}\n\n"
    error_text += f"Traceback:\n```\n{traceback.format_exc()[:500]}\n```"
    
    try:
        from src.bot.loader import bot
        await bot.send_message(chat_id=settings.ADMIN_ID, text=error_text, parse_mode="Markdown")
    except:
        pass
