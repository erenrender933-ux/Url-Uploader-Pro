import os

from pyrogram import Client, filters
from pyrogram.types import Message

from config import THUMB_DIR
from database import update_setting
from helpers.thumbnail import prepare_thumb


@Client.on_message(filters.command("setthumb") & filters.private & filters.reply)
async def set_thumb(client: Client, message: Message):
    replied = message.reply_to_message
    if not replied.photo:
        return await message.reply_text("Reply to a photo with /setthumb.")

    os.makedirs(THUMB_DIR, exist_ok=True)
    uid = message.from_user.id
    raw_path = os.path.join(THUMB_DIR, f"{uid}_raw")
    final_path = os.path.join(THUMB_DIR, f"{uid}.jpg")

    await client.download_media(replied.photo.file_id, file_name=raw_path)
    try:
        prepare_thumb(raw_path, final_path)
    except Exception as e:
        return await message.reply_text(f"Could not process this image: {e}")
    finally:
        if os.path.exists(raw_path):
            os.remove(raw_path)

    await update_setting(uid, "thumb", final_path)
    await message.reply_text("Thumbnail saved.")


@Client.on_message(filters.command("delthumb") & filters.private)
async def del_thumb(client: Client, message: Message):
    thumb_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    if os.path.exists(thumb_path):
        os.remove(thumb_path)
    await update_setting(message.from_user.id, "thumb", None)
    await message.reply_text("Thumbnail removed.")
