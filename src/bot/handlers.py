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
            [InlineKeyboardButton(text="📋 Guruhlar", callback_data="list_groups")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats")],
            [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
        ])
        await message.answer(f"Assalomu alaykum, Admin! 👋\n\nBoshqaruv paneli:", reply_markup=keyboard)
    else:
        await message.answer(f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\nMen **Taxi Bot** man 🚕.")


@router.callback_query(F.data == "show_stats")
async def show_stats(callback: CallbackQuery):
    db = next(get_db())
    count = db.query(Log).count()
    passengers = db.query(Log).filter(Log.is_passenger == True).count()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
    ])
    
    await callback.message.edit_text(f"📊 **Statistika**\n\nJami Xabarlar: {count}\nYo'lovchilar: {passengers}", parse_mode="Markdown", reply_markup=keyboard)
    db.close()

@router.callback_query(F.data == "list_groups")
async def list_groups(callback: CallbackQuery):
    db = next(get_db())
    groups = db.query(SourceGroup).all()
    text = "📋 **Kuzatilayotgan Guruhlar:**\n\n"
    
    keyboard_buttons = []
    for g in groups:
        status = "✅" if g.active else "❌"
        text += f"{status} `{g.chat_id}` - {g.name or 'Nomalum'}\n"
        keyboard_buttons.append([InlineKeyboardButton(text=f"{status} {g.name or g.chat_id}", callback_data=f"group_{g.id}")])
    
    if not groups:
        text += "Guruhlar mavjud emas."
    
    keyboard_buttons.append([InlineKeyboardButton(text="➕ Guruh Qo'shish (/add)", callback_data="add_help")])
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    db.close()

@router.callback_query(F.data == "add_help")
async def add_help(callback: CallbackQuery):
    text = "➕ **Guruh Qo'shish:**\n\n"
    text += "Foydalanish: `/add <chat_id> <nomi>`\n\n"
    text += "Misol: `/add -1001234567890 Namangan Taksi`"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="list_groups")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data.startswith("group_"))
async def group_detail(callback: CallbackQuery):
    group_id = int(callback.data.split("_")[1])
    db = next(get_db())
    group = db.query(SourceGroup).filter(SourceGroup.id == group_id).first()
    
    if not group:
        await callback.answer("Guruh topilmadi")
        return
    
    status = "✅ Faol" if group.active else "❌ Nofaol"
    text = f"📋 **Guruh Ma'lumotlari:**\n\n"
    text += f"Nomi: {group.name or 'Nomalum'}\n"
    text += f"Chat ID: `{group.chat_id}`\n"
    text += f"Holat: {status}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Holatni O'zgartirish", callback_data=f"toggle_{group_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_{group_id}")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="list_groups")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    db.close()

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_group(callback: CallbackQuery):
    group_id = int(callback.data.split("_")[1])
    db = next(get_db())
    group = db.query(SourceGroup).filter(SourceGroup.id == group_id).first()
    
    if group:
        group.active = not group.active
        db.commit()
        await callback.answer(f"Guruh {'faollashtirildi' if group.active else 'nofaol qilindi'}")
    
    db.close()
    callback.data = f"group_{group_id}"
    await group_detail(callback)

@router.callback_query(F.data.startswith("delete_"))
async def delete_group(callback: CallbackQuery):
    group_id = int(callback.data.split("_")[1])
    db = next(get_db())
    group = db.query(SourceGroup).filter(SourceGroup.id == group_id).first()
    
    if group:
        db.delete(group)
        db.commit()
        await callback.answer("Guruh o'chirildi")
    
    db.close()
    callback.data = "list_groups"
    await list_groups(callback)

@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery):
    text = f"⚙️ **Sozlamalar:**\n\n"
    text += f"Buyurtmalar Guruhi: `{settings.TARGET_GROUP_ID}`\n"
    text += f"AI Model: {settings.OPENAI_MODEL}\n"
    text += f"Admin ID: `{settings.ADMIN_ID}`\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Guruhlar", callback_data="list_groups")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
    ])
    await callback.message.edit_text(f"Assalomu alaykum, Admin! 👋\n\nBoshqaruv paneli:", reply_markup=keyboard)

@router.message(Command("add"))
async def add_group_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Foydalanish: `/add <chat_id> <nomi>`", parse_mode="Markdown")
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
    await message.answer(f"✅ Guruh qo'shildi: {name} (`{chat_id}`)", parse_mode="Markdown")

@router.message(Command("stats"))
async def stats_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    db = next(get_db())
    count = db.query(Log).count()
    passengers = db.query(Log).filter(Log.is_passenger == True).count()
    await message.answer(f"📊 **Statistika**\n\nJami Xabarlar: {count}\nYo'lovchilar: {passengers}", parse_mode="Markdown")
    db.close()
