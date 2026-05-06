import os

# Your Telegram Bot Token from @BotFather
BOT_TOKEN = "8787806284:AAEI0V5XNzl0x2Y-hsjnQN9YsDd2PMMukyw"

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
         "id": "@kinoplay_4k", 
         "url": "https://t.me/kinoplay_4k", 
         "name": "Kanal 1"
     },
]

# Database file
DB_PATH = "movies.db"
