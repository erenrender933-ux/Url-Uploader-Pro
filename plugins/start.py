from pyrogram import Client, filters
from pyrogram.types import Message

from config import OWNER_ID
from database import add_user, total_users
from helpers.fsub import FSUB_TEXT, fsub_keyboard, get_missing_channels


@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    await add_user(message.from_user.id, message.from_user.first_name or "User")

    try:
        missing = await get_missing_channels(client, message.from_user.id)
    except Exception:
        return await message.reply_text("Bot config error. Please contact the owner.")

    if missing:
        return await message.reply_text(FSUB_TEXT, reply_markup=fsub_keyboard(missing))

    await message.reply_text(
        f"Hi {message.from_user.first_name}!\n\n"
        "Send me a Google Drive link or a direct download link and I will "
        "download the file and upload it to this chat.\n\n"
        "Use /settings to change the renamer, format, audio track, metadata and thumbnail."
    )


@Client.on_message(filters.command("stats") & filters.private & filters.user(OWNER_ID))
async def stats_cmd(client: Client, message: Message):
    count = await total_users()
    await message.reply_text(f"Total users: {count}")
