import os

# Your Telegram Bot Token from @BotFather
BOT_TOKEN = "8640151765:AAE2Xg9m7Q4_RAhRrL4UgqEza2C_TM-pCzo"

# Adminlar Telegram ID raqamlari
ADMIN_IDS = [
    6547348382,
    8235070957,
    7964686556,
    6471396425
]

# List of mandatory channels
# Format: {"id": "-100123456789", "url": "https://t.me/yourchannel", "name": "Kanal nomi"}
MANDATORY_CHANNELS = [
    # Replace with your actual channel IDs and URLs
     {
         "id": "@a21dev", 
         "url": "https://t.me/a21dev", 
         "name": "Kanal 1"
     },
     {
         "id": "@kinoplay_4k", 
         "url": "https://t.me/kinoplay_4k", 
         "name": "Kanal 2"
     },
]

# Database file
DB_PATH = "movies.db"
