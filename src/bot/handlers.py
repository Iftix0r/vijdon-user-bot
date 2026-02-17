from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from src.database.models import get_db, SourceGroup, Log
from src.config import settings

router = Router()

# Simple admin check
ADMIN_IDS = [settings.ADMIN_ID]

@router.message(Command("start"))
async def start_handler(message: Message):
    if message.from_user.id in ADMIN_IDS:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Guruhlar Ro'yxati", callback_data="list_groups")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats")],
        ])
        await message.answer(f"Assalomu alaykum, Admin! 👋\n\nBoshqaruv paneli:", reply_markup=keyboard)
    else:
        await message.answer(f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\nMen **Taxi Bot** man 🚕.")


@router.callback_query(F.data == "show_stats")
async def show_stats(callback: CallbackQuery):
    db = next(get_db())
    count = db.query(Log).count()
    passengers = db.query(Log).filter(Log.is_passenger == True).count()
    await callback.message.edit_text(f"📊 **Statistika**\n\nJami Xabarlar: {count}\nYo'lovchilar: {passengers}")
    db.close()


@router.callback_query(F.data == "list_groups")
async def list_groups(callback: CallbackQuery):
    db = next(get_db())
    groups = db.query(SourceGroup).all()
    text = "📋 **Kuzatilayotgan Guruhlar:**\n\n"
    for g in groups:
        status = "✅" if g.active else "❌"
        text += f"{status} `{g.chat_id}` - {g.name or 'Noma\'lum'}\n"
    
    if not groups:
        text += "Guruhlar mavjud emas."
        
    await callback.message.edit_text(text, parse_mode="Markdown")
    db.close()

# For add_group/remove_group, we'd need FSM or simple "Reply with ID" logic.
# For brevity, let's just make it simple command based: /add <id> <name>
@router.message(Command("add"))
async def add_group_cmd(message: Message):
    # expect /add -100123123123 NamanganTaksi
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: `/add <chat_id> <nomi>`")
        return
    
    chat_id = args[1]
    name = " ".join(args[2:]) if len(args) > 2 else "Adsiz Guruh"
    
    db = next(get_db())
    existing = db.query(SourceGroup).filter(SourceGroup.chat_id == chat_id).first()
    if existing:
        existing.active = True
        existing.name = name
    else:
        new_group = SourceGroup(chat_id=chat_id, name=name, active=True)
        db.add(new_group)
    
    db.commit()
    db.close()
    await message.answer(f"✅ Guruh qo'shildi: {name} (`{chat_id}`)")

@router.message(Command("stats"))
async def stats_cmd(message: Message):
    db = next(get_db())
    count = db.query(Log).count()
    passengers = db.query(Log).filter(Log.is_passenger == True).count()
    await message.answer(f"📊 **Statistika**\n\nJami Xabarlar: {count}\nYo'lovchilar: {passengers}")
    db.close()
