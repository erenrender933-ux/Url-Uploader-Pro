import asyncio
import os
import shutil
import uuid

from pyrogram import Client, filters
from pyrogram.types import Message

from config import DOWNLOAD_DIR, MAX_CONCURRENT_TASKS, MAX_FILE_SIZE
from database import add_user, get_settings
from helpers.downloader import download
from helpers.ffmpeg import process_file
from helpers.progress import Progress, safe_edit
from helpers.renamer import DEFAULT_FORMAT, build_name
from helpers.thumbnail import prepare_thumb

task_limit = asyncio.Semaphore(MAX_CONCURRENT_TASKS)


@Client.on_message(filters.private & filters.text & filters.regex(r"^https?://\S+$"))
async def url_handler(client: Client, message: Message):
    user_id = message.from_user.id
    await add_user(user_id, message.from_user.first_name or "User")

    url = message.text.strip()
    settings = await get_settings(user_id)
    status = await message.reply_text("Queued...")

    # Each task gets its own folder so file names never collide
    task_dir = os.path.join(DOWNLOAD_DIR, uuid.uuid4().hex)
    os.makedirs(task_dir, exist_ok=True)

    async with task_limit:
        try:
            downloaded = await download(url, status)

            source = os.path.join(task_dir, os.path.basename(downloaded))
            shutil.move(downloaded, source)

            original_name = os.path.basename(source)
            if settings.get("renamer", True):
                name = build_name(settings.get("format", DEFAULT_FORMAT), original_name)
            else:
                name = original_name

            output = os.path.join(task_dir, name)
            audio_track = settings.get("audio_track")
            title = settings.get("metadata_title")
            needs_processing = audio_track is not None or bool(title)

            if needs_processing:
                await safe_edit(status, "**Processing file...**")
                await process_file(source, output, audio_track=audio_track, title=title)
            else:
                os.replace(source, output)

            if os.path.getsize(output) > MAX_FILE_SIZE:
                raise ValueError("File is larger than 4 GB.")

            # Thumbnail: convert to Telegram format. If it fails, upload without it.
            thumb = None
            saved_thumb = settings.get("thumb")
            if saved_thumb and os.path.exists(saved_thumb):
                thumb = os.path.join(task_dir, "thumb.jpg")
                try:
                    prepare_thumb(saved_thumb, thumb)
                except Exception:
                    thumb = None

            await message.reply_document(
                document=output,
                file_name=name,
                caption=name,
                thumb=thumb,
                progress=Progress(status, "Uploading"),
            )
            await status.delete()

        except Exception as e:
            await safe_edit(status, f"Error: {e}")

        finally:
            shutil.rmtree(task_dir, ignore_errors=True)
