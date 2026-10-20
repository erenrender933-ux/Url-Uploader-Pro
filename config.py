import os

from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "UrlUploaderBot")

DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "downloads")
THUMB_DIR = os.environ.get("THUMB_DIR", "thumbs")

# Telegram upload limit for premium accounts is 4 GB
MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024

# How many files can be downloaded/processed/uploaded at the same time
MAX_CONCURRENT_TASKS = int(os.environ.get("MAX_CONCURRENT_TASKS", "2"))

# Force-subscribe channels.
# Use "@username" for public channels, or the numeric ID (-100...) for private ones.
# The bot must be an admin in every channel listed here.
# Leave the list empty to turn force-subscribe off.
FSUB_CHANNELS = [
    "-1002649539214",
    "-1003766203099",
]
