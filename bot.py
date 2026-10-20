import os
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from pyrogram import Client

from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_DIR, THUMB_DIR

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

app = Client(
    "UrlUploaderBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
