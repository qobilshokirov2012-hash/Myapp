import os

BOT_TOKEN = os.getenv("BOT_MAFIA")
MONGO_URL = os.getenv("MONGO_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
