from pyrogram import Client, filters
from pyrogram.types import Message

from database import get_settings, update_setting
from helpers.renamer import DEFAULT_FORMAT

ALLOWED_FIELDS = ("title", "season", "episode", "quality")


def _onoff(value: bool) -> str:
    return "ON" if value else "OFF"


@Client.on_message(filters.command("settings") & filters.private)
async def show_settings(client: Client, message: Message):
    s = await get_settings(message.from_user.id)
    track = s.get("audio_track")
    await message.reply_text(
        "Your settings\n\n"
        f"Renamer: {_onoff(s.get('renamer', True))}\n"
        f"Format: {s.get('format', DEFAULT_FORMAT)}\n"
        f"Audio track kept: {track if track else 'OFF (all tracks kept)'}\n"
        f"Metadata title: {s.get('metadata_title') or 'None'}\n"
        f"Thumbnail: {'Set' if s.get('thumb') else 'None'}\n\n"
        "Commands:\n"
        "/renameron or /renameroff\n"
        "/setformat {title} S{season}E{episode} [{quality}]\n"
        "/keepaudio 1 (keep first audio only)\n"
        "/keepaudio 2 (keep second audio only)\n"
        "/keepaudio off\n"
        "/metadata <title>  (send /metadata alone to clear)\n"
        "/setthumb  (reply to a photo)\n"
        "/delthumb"
    )


@Client.on_message(filters.command("renameron") & filters.private)
async def rename_on(client: Client, message: Message):
    await update_setting(message.from_user.id, "renamer", True)
    await message.reply_text("Renamer is ON.")


@Client.on_message(filters.command("renameroff") & filters.private)
async def rename_off(client: Client, message: Message):
    await update_setting(message.from_user.id, "renamer", False)
    await message.reply_text("Renamer is OFF. Original file names will be kept.")


@Client.on_message(filters.command("setformat") & filters.private)
async def set_format(client: Client, message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply_text(
            "Usage: /setformat {title} S{season}E{episode} [{quality}]"
        )

    fmt = parts[1].strip()
    try:
        fmt.format(title="x", season="01", episode="01", quality="720p")
    except (KeyError, IndexError, ValueError) as e:
        allowed = ", ".join("{" + f + "}" for f in ALLOWED_FIELDS)
        return await message.reply_text(f"Invalid format: {e}. Allowed fields: {allowed}")

    await update_setting(message.from_user.id, "format", fmt)
    await message.reply_text(f"Format saved:\n{fmt}")


@Client.on_message(filters.command("keepaudio") & filters.private)
async def keep_audio(client: Client, message: Message):
    parts = message.text.split()
    value = parts[1].lower() if len(parts) > 1 else ""

    if value not in ("1", "2", "off"):
        return await message.reply_text(
            "Usage:\n"
            "/keepaudio 1  (keep first audio only)\n"
            "/keepaudio 2  (keep second audio only)\n"
            "/keepaudio off"
        )

    if value == "off":
        await update_setting(message.from_user.id, "audio_track", None)
        return await message.reply_text("Audio filter OFF. All audio and subtitles will be kept.")

    track = int(value)
    await update_setting(message.from_user.id, "audio_track", track)
    await message.reply_text(
        f"Only audio track {track} will be kept. "
        "Other audio, subtitles and streams will be removed."
    )


@Client.on_message(filters.command("metadata") & filters.private)
async def metadata_cmd(client: Client, message: Message):
    parts = message.text.split(maxsplit=1)
    value = parts[1].strip() if len(parts) > 1 else None
    await update_setting(message.from_user.id, "metadata_title", value)
    await message.reply_text(f"Metadata title: {value or 'cleared'}")
