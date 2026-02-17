from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from src.database.models import get_db, SourceGroup, Log
from src.config import settings
from src.bot.states import TelegramLogin

router = Router()

# Simple admin check
ADMIN_IDS = [settings.ADMIN_ID]

@router.message(Command("start"))
async def start_handler(message: Message):
    if message.from_user.id in ADMIN_IDS:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Guruhlar", callback_data="list_groups")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats")],
            [InlineKeyboardButton(text="🔗 Telegram Ulash", callback_data="connect_telegram")],
            [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
            [InlineKeyboardButton(text="📢 Broadcast", callback_data="broadcast_help")],
        ])
        await message.answer(f"Assalomu alaykum, Admin! 👋\n\nBoshqaruv paneli:", reply_markup=keyboard)
    else:
        await message.answer(f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\nMen **Taxi Bot** man 🚕.")


@router.callback_query(F.data == "show_stats")
async def show_stats(callback: CallbackQuery):
    db = next(get_db())
    total_logs = db.query(Log).count()
    passengers = db.query(Log).filter(Log.is_passenger == True).count()
    drivers = total_logs - passengers
    
    # Guruhlar statistikasi
    active_groups = db.query(SourceGroup).filter(SourceGroup.active == True).count()
    total_groups = db.query(SourceGroup).count()
    
    text = "📊 **Statistika**\n\n"
    text += f"📨 Jami Xabarlar: {total_logs}\n"
    text += f"👤 Yo'lovchilar: {passengers}\n"
    text += f"🚗 Haydovchilar: {drivers}\n\n"
    text += f"📋 Guruhlar: {active_groups}/{total_groups} faol\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yangilash", callback_data="show_stats")],
        [InlineKeyboardButton(text="🗑 Loglarni Tozalash", callback_data="clear_logs")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    db.close()

@router.callback_query(F.data == "list_groups")
async def list_groups(callback: CallbackQuery):
    db = next(get_db())
    groups = db.query(SourceGroup).all()
    
    active_count = sum(1 for g in groups if g.active)
    text = f"📋 **Guruhlar ({active_count}/{len(groups)} faol):**\n\n"
    
    keyboard_buttons = []
    for g in groups:
        status = "✅" if g.active else "❌"
        name_display = g.name[:20] if g.name else str(g.chat_id)[:15]
        keyboard_buttons.append([InlineKeyboardButton(text=f"{status} {name_display}", callback_data=f"group_{g.id}")])
    
    if not groups:
        text += "Guruhlar mavjud emas.\n\n"
        text += "ℹ️ Guruh qo'shish uchun `/add` buyrug'idan foydalaning."
    
    keyboard_buttons.append([InlineKeyboardButton(text="➕ Guruh Qo'shish", callback_data="add_help")])
    keyboard_buttons.append([InlineKeyboardButton(text="🔄 Yangilash", callback_data="list_groups")])
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
    
    # Guruh statistikasi
    group_logs = db.query(Log).filter(Log.source_chat_id == group.chat_id).count()
    
    status = "✅ Faol" if group.active else "❌ Nofaol"
    text = f"📋 **Guruh Tafsilotlari:**\n\n"
    text += f"🏷 Nomi: {group.name or 'Nomalum'}\n"
    text += f"🆔 Chat ID: `{group.chat_id}`\n"
    text += f"🟢 Holat: {status}\n"
    text += f"📨 Xabarlar: {group_logs}\n"
    
    toggle_text = "❌ Nofaol Qilish" if group.active else "✅ Faollashtirish"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=toggle_text, callback_data=f"toggle_{group_id}")],
        [InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"group_{group_id}")],
        [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"confirm_delete_{group_id}")],
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

@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_group(callback: CallbackQuery):
    group_id = int(callback.data.split("_")[2])
    db = next(get_db())
    group = db.query(SourceGroup).filter(SourceGroup.id == group_id).first()
    
    if not group:
        await callback.answer("Guruh topilmadi")
        return
    
    text = f"⚠️ **Guruhni o'chirish:**\n\n"
    text += f"Guruh: {group.name or 'Nomalum'}\n"
    text += f"Chat ID: `{group.chat_id}`\n\n"
    text += "Rostdan ham o'chirmoqchimisiz?"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, O'chirish", callback_data=f"delete_{group_id}")],
        [InlineKeyboardButton(text="❌ Bekor Qilish", callback_data=f"group_{group_id}")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    db.close()

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

@router.callback_query(F.data == "clear_logs")
async def clear_logs(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, Tozalash", callback_data="confirm_clear_logs")],
        [InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="show_stats")],
    ])
    await callback.message.edit_text("⚠️ **Barcha loglarni o'chirmoqchimisiz?**\n\nBu amalni qaytarib bo'lmaydi!", parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data == "confirm_clear_logs")
async def confirm_clear_logs(callback: CallbackQuery):
    db = next(get_db())
    count = db.query(Log).count()
    db.query(Log).delete()
    db.commit()
    db.close()
    
    await callback.answer(f"{count} ta log o'chirildi")
    callback.data = "show_stats"
    await show_stats(callback)

@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery):
    db = next(get_db())
    total_logs = db.query(Log).count()
    db.close()
    
    text = f"⚙️ **Sozlamalar:**\n\n"
    text += f"📤 Buyurtmalar Guruhi: `{settings.TARGET_GROUP_ID}`\n"
    text += f"🤖 AI Model: {settings.OPENAI_MODEL}\n"
    text += f"👤 Admin ID: `{settings.ADMIN_ID}`\n"
    text += f"💾 Database: {total_logs} yozuv\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Tizim Ma'lumotlari", callback_data="system_info")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data == "connect_telegram")
async def connect_telegram(callback: CallbackQuery, state: FSMContext):
    import os
    
    session_exists = os.path.exists('userbot_session.session')
    
    if session_exists:
        text = "📱 **Telegram Akkaunti:**\n\n"
        text += "✅ Akkount ulangan\n\n"
        text += "Nima qilmoqchisiz?"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Boshqa Akkaunt", callback_data="reconnect_telegram")],
            [InlineKeyboardButton(text="🚪 Chiqish", callback_data="logout_telegram")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
        ])
    else:
        text = "📱 **Telegram Akkauntga Kirish:**\n\n"
        text += "Telefon raqamingizni kiriting\n"
        text += "Misol: +998901234567"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="back_main")],
        ])
        
        await state.set_state(TelegramLogin.waiting_for_phone)
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data == "reconnect_telegram")
async def reconnect_telegram(callback: CallbackQuery, state: FSMContext):
    text = "📱 **Yangi Akkauntga Kirish:**\n\n"
    text += "Telefon raqamingizni kiriting\n"
    text += "Misol: +998901234567"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor Qilish", callback_data="connect_telegram")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await state.set_state(TelegramLogin.waiting_for_phone)

@router.callback_query(F.data == "logout_telegram")
async def logout_telegram(callback: CallbackQuery):
    import os
    
    try:
        if os.path.exists('userbot_session.session'):
            os.remove('userbot_session.session')
        if os.path.exists('userbot_session.session-journal'):
            os.remove('userbot_session.session-journal')
        
        text = "✅ Akkauntdan chiqildi!\n\n"
        text += "Botni qayta ishga tushiring: /restart"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
        ])
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        await callback.answer(f"❌ Xato: {str(e)}")

@router.message(TelegramLogin.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    phone = message.text.strip()
    
    try:
        from telethon import TelegramClient
        from src.config import settings
        
        client = TelegramClient('admin_session', settings.API_ID, settings.API_HASH)
        await client.connect()
        
        result = await client.send_code_request(phone)
        
        await state.update_data(phone=phone, phone_code_hash=result.phone_code_hash, client=client)
        await state.set_state(TelegramLogin.waiting_for_code)
        
        text = "✅ Kod yuborildi!\n\n"
        text += "📝 Kodni quyidagi formatda kiriting:\n"
        text += "Misol: `12345` yoki `1.2.3.4.5`\n\n"
        text += "⚠️ Diqqat: Kod 5 daqiqa ichida amal qiladi!\n\n"
        text += "Agar kod muddati tugasa, qaytadan `/start` bosib yangi kod oling."
        
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)}")
        await state.clear()

@router.message(TelegramLogin.waiting_for_code)
async def process_code(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    code = message.text.strip().replace(".", "").replace(" ", "").replace("-", "")
    data = await state.get_data()
    
    try:
        client = data['client']
        phone = data['phone']
        
        await client.sign_in(phone, code)
        
        # Save session
        await client.disconnect()
        
        await message.answer("✅ Muvaffaqiyatli kirildi! Botni qayta ishga tushiring: /restart")
        await state.clear()
    except Exception as e:
        error_msg = str(e)
        if "password" in error_msg.lower():
            await state.set_state(TelegramLogin.waiting_for_password)
            await message.answer("🔐 2FA parol kiriting:")
        elif "expired" in error_msg.lower():
            await message.answer("❌ Kod muddati tugagan! Qaytadan `/start` bosib yangi kod oling.", parse_mode="Markdown")
            await state.clear()
        else:
            await message.answer(f"❌ Xato: {error_msg}\n\nQaytadan urinib ko'ring yoki `/start` bosing.", parse_mode="Markdown")
            await state.clear()

@router.message(TelegramLogin.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    password = message.text.strip()
    data = await state.get_data()
    
    try:
        client = data['client']
        await client.sign_in(password=password)
        await client.disconnect()
        
        await message.answer("✅ Muvaffaqiyatli kirildi! Botni qayta ishga tushiring: /restart")
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)}")
        await state.clear()

@router.message(Command("settoken"))
async def set_token_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Foydalanish: `/settoken <bot_token>`", parse_mode="Markdown")
        return
    
    token = args[1]
    
    # Token ni .env ga yozish
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
        
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("BOT_TOKEN="):
                    f.write(f"BOT_TOKEN={token}\n")
                else:
                    f.write(line)
        
        await message.answer("✅ Token saqlandi! Botni qayta ishga tushiring: `/restart`", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Xato: {str(e)}")

@router.message(Command("restart"))
async def restart_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    await message.answer("🔄 Bot qayta ishga tushirilmoqda...")
    import os
    import sys
    os.execv(sys.executable, ['python3'] + sys.argv)

@router.callback_query(F.data == "system_info")
async def system_info(callback: CallbackQuery):
    import platform
    import psutil
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    text = f"💻 **Tizim Ma'lumotlari:**\n\n"
    text += f"💿 OS: {platform.system()} {platform.release()}\n"
    text += f"🔹 Python: {platform.python_version()}\n"
    text += f"🟢 CPU: {cpu_percent}%\n"
    text += f"🟡 RAM: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)\n"
    text += f"🟠 Disk: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yangilash", callback_data="system_info")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data == "broadcast_help")
async def broadcast_help(callback: CallbackQuery):
    text = "📢 **Broadcast:**\n\n"
    text += "Barcha faol guruhlarga xabar yuborish\n\n"
    text += "Foydalanish: `/broadcast <xabar>`\n\n"
    text += "Misol: `/broadcast Botda texnik ishlar`"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main")],
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)

@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Guruhlar", callback_data="list_groups")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="show_stats")],
        [InlineKeyboardButton(text="🔗 Telegram Ulash", callback_data="connect_telegram")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="broadcast_help")],
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

@router.message(Command("help"))
async def help_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    text = """
📖 **Yordam**

**Admin Komandalar:**
/start - Boshqaruv paneli
/add <chat_id> <nomi> - Guruh qo'shish
/stats - Statistika
/broadcast <xabar> - Barcha guruhlarga xabar yuborish
/help - Yordam

**Misol:**
`/add -1001234567890 Namangan Taksi`
`/broadcast Botda texnik ishlar olib borilmoqda`

**Bot Funksiyalari:**
✅ Guruhlarni kuzatish
✅ AI orqali buyurtmalarni aniqlash
✅ Haydovchilar guruhiga yuborish
✅ Statistika va hisobotlar
"""
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("broadcast"))
async def broadcast_cmd(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("Foydalanish: `/broadcast <xabar>`", parse_mode="Markdown")
        return
    
    db = next(get_db())
    groups = db.query(SourceGroup).filter(SourceGroup.active == True).all()
    
    success = 0
    failed = 0
    
    status_msg = await message.answer("📤 Xabar yuborilmoqda...")
    
    for group in groups:
        try:
            await message.bot.send_message(chat_id=group.chat_id, text=text)
            success += 1
        except Exception as e:
            failed += 1
            print(f"Broadcast error to {group.chat_id}: {e}")
    
    db.close()
    await status_msg.edit_text(f"✅ Xabar yuborildi:\n\nMuvaffaqiyatli: {success}\nXato: {failed}")
