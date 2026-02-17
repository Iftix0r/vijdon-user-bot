from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.models import get_db, Log

order_router = Router()

@order_router.callback_query(F.data.startswith("accept_"))
async def accept_order(callback: CallbackQuery):
    order_id = callback.data.split("_")[1]
    
    db = next(get_db())
    log = db.query(Log).filter(Log.id == int(order_id)).first()
    
    if log:
        driver_name = callback.from_user.full_name
        driver_username = f"@{callback.from_user.username}" if callback.from_user.username else ""
        
        response = f"✅ **Buyurtma Qabul Qilindi!**\n\n"
        response += f"🚗 Haydovchi: {driver_name} {driver_username}\n"
        response += f"📞 Aloqa: {driver_username or 'Telefon raqam'}\n\n"
        response += "Mijoz bilan bog'laning!"
        
        await callback.message.edit_text(response, parse_mode="Markdown")
        await callback.answer("✅ Buyurtma qabul qilindi!")
    else:
        await callback.answer("❌ Buyurtma topilmadi")
    
    db.close()

@order_router.callback_query(F.data.startswith("reject_"))
async def reject_order(callback: CallbackQuery):
    await callback.message.edit_text("❌ Buyurtma rad etildi")
    await callback.answer("Buyurtma rad etildi")
