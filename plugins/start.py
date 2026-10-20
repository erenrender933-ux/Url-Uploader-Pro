from pyrogram import Client, filters
from pyrogram.types import Message

from config import OWNER_ID
from database import add_user, total_users


@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    await add_user(message.from_user.id, message.from_user.first_name or "User")
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
