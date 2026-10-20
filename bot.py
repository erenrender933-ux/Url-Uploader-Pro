import logging
import os

from pyrogram import Client

from config import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_DIR, THUMB_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

SESSION_DIR = "/app/sessions"
os.makedirs(SESSION_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

# Absolute name, so the session file is stored in the mounted folder.
# Plugins are still loaded from /app/plugins because workdir is unchanged.
app = Client(
    os.path.join(SESSION_DIR, "UrlUploaderBot"),
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
