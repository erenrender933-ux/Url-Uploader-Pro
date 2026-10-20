import asyncio
import logging
import os
import shutil
import uuid

from pyrogram import Client, filters
from pyrogram.types import Message

from config import DOWNLOAD_DIR, MAX_CONCURRENT_TASKS, MAX_FILE_SIZE
from database import add_user, get_settings
from helpers.downloader import download
from helpers.ffmpeg import process_file
from helpers.fsub import FSUB_TEXT, fsub_keyboard, get_missing_channels
from helpers.progress import Progress, safe_edit
from helpers.renamer import DEFAULT_FORMAT, build_name
from helpers.thumbnail import prepare_thumb

log = logging.getLogger("url_upload")
task_limit = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

PROCESS_TIMEOUT = 60 * 60   # 1 hour max for ffmpeg
UPLOAD_TIMEOUT = 60 * 60    # 1 hour max for upload


@Client.on_message(filters.private & filters.text & filters.regex(r"^https?://\S+$"))
async def url_handler(client: Client, message: Message):
    user_id = message.from_user.id
    await add_user(user_id, message.from_user.first_name or "User")

    try:
        missing = await get_missing_channels(client, user_id)
    except Exception:
        return await message.reply_text("Bot config error. Please contact the owner.")

    if missing:
        return await message.reply_text(FSUB_TEXT, reply_markup=fsub_keyboard(missing))

    url = message.text.strip()
    settings = await get_settings(user_id)
    status = await message.reply_text("Queued...")
    log.info("[%s] task queued: %s", user_id, url)

    task_dir = os.path.join(DOWNLOAD_DIR, uuid.uuid4().hex)
    os.makedirs(task_dir, exist_ok=True)

    async with task_limit:
        try:
            # Stage 1: download
            log.info("[%s] stage 1: download start", user_id)
            downloaded = await download(url, status)
            log.info("[%s] stage 1: download done -> %s", user_id, downloaded)

            source = os.path.join(task_dir, os.path.basename(downloaded))
            shutil.move(downloaded, source)

            # Stage 2: rename (AniList lookup)
            log.info("[%s] stage 2: rename start", user_id)
            original_name = os.path.basename(source)
            if settings.get("renamer", True):
                name = await build_name(settings.get("format", DEFAULT_FORMAT), original_name)
            else:
                name = original_name
            log.info("[%s] stage 2: rename done -> %s", user_id, name)

            output = os.path.join(task_dir, name)
            audio_track = settings.get("audio_track")
            title = settings.get("metadata_title")
            needs_processing = audio_track is not None or bool(title)

            # Stage 3: ffmpeg processing (audio track / metadata)
            if needs_processing:
                log.info("[%s] stage 3: processing start", user_id)
                await safe_edit(status, "Processing file...")
                await asyncio.wait_for(
                    process_file(source, output, audio_track=audio_track, title=title),
                    timeout=PROCESS_TIMEOUT,
                )
                log.info("[%s] stage 3: processing done", user_id)
            else:
                os.replace(source, output)

            if os.path.getsize(output) > MAX_FILE_SIZE:
                raise ValueError("File is larger than 4 GB.")

            # Stage 4: thumbnail
            thumb = None
            saved_thumb = settings.get("thumb")
            if saved_thumb and os.path.exists(saved_thumb):
                thumb = os.path.join(task_dir, "thumb.jpg")
                try:
                    prepare_thumb(saved_thumb, thumb)
                except Exception as e:
                    log.warning("[%s] thumbnail skipped: %s", user_id, e)
                    thumb = None

            # Stage 5: upload
            log.info("[%s] stage 5: upload start", user_id)
            await asyncio.wait_for(
                message.reply_document(
                    document=output,
                    file_name=name,
                    caption=name,
                    thumb=thumb,
                    progress=Progress(status, "Uploading"),
                ),
                timeout=UPLOAD_TIMEOUT,
            )
            log.info("[%s] stage 5: upload done", user_id)
            await status.delete()

        except asyncio.TimeoutError:
            log.error("[%s] timed out", user_id)
            await safe_edit(status, "Error: timed out. Try a smaller file.")
        except Exception as e:
            log.exception("[%s] task failed", user_id)
            await safe_edit(status, f"Error: {e}")

        finally:
            shutil.rmtree(task_dir, ignore_errors=True)
