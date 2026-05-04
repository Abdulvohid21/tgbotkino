import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router
import database

async def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Iltimos, config.py faylida BOT_TOKEN ni o'rnating!")
        sys.exit(1)
        
    # Initialize DB
    await database.init_db()

    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Include router
    dp.include_router(router)
    
    print("Bot ishga tushdi...")
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi!")
