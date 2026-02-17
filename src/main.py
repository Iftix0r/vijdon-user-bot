import asyncio
import logging
import sys
import uvicorn
from dotenv import load_dotenv
from telethon import TelegramClient, events
from aiogram import Dispatcher
from src.config import settings
from src.bot.loader import bot, dp
from src.bot.handlers import router
from src.userbot.handler import handle_new_message
from src.web.server import app

# Load .env
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Telethon Client
client = TelegramClient('userbot_session', settings.API_ID, settings.API_HASH)

async def start_userbot():
    logger.info("Starting Userbot...")
    await client.start(phone=lambda: input("Please enter your phone (or bot token): "))
    
    # Register handlers
    client.add_event_handler(handle_new_message, events.NewMessage(incoming=True))
    
    logger.info("Userbot started and listening...")
    await client.run_until_disconnected()

async def start_bot():
    logger.info("Starting Bot...")
    dp.include_router(router)
    await dp.start_polling(bot)

async def start_web():
    logger.info("Starting Web Admin Panel on port 8000...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    logger.info("Initializing services...")
    
    # Run them concurrently
    await asyncio.gather(
        start_userbot(),
        start_bot(),
        start_web(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
