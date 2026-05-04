import os

# Your Telegram Bot Token from @BotFather
BOT_TOKEN = "8640151765:AAE2Xg9m7Q4_RAhRrL4UgqEza2C_TM-pCzo"

# Admin's Telegram ID
ADMIN_ID = 0  # Shu yerga o'zingizning Telegram ID raqamingizni yozing (masalan: 123456789)

# List of mandatory channels
# Format: {"id": "-100123456789", "url": "https://t.me/yourchannel", "name": "Kanal nomi"}
MANDATORY_CHANNELS = [
    # Replace with your actual channel IDs and URLs
     {
         "id": "@a21dev", 
         "url": "https://t.me/a21dev", 
         "name": "Kanal 1"
     },
]

# Database file
DB_PATH = "movies.db"
