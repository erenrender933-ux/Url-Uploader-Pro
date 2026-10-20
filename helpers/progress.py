import asyncio
import logging
import time

from pyrogram.enums import ParseMode
from pyrogram.errors import MessageNotModified

log = logging.getLogger("progress")


def human_size(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"


def format_time(seconds: float) -> str:
    seconds = int(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def progress_text(action: str, current: int, total: int, start: float) -> str:
    elapsed = max(time.time() - start, 0.1)
    speed = current / elapsed
    percent = current * 100 / total if total else 0
    filled = min(int(percent // 10), 10)
    bar = "■" * filled + "□" * (10 - filled)
    eta = (total - current) / speed if speed and total else 0
    icon = "📥" if action == "Downloading" else "📤"
    return (
        f"<b>{icon} {action}\n\n"
        f"{bar} {percent:.1f}%\n\n"
        f"📦 Size: {human_size(current)} / {human_size(total)}\n"
        f"⚡ Speed: {human_size(speed)}/s\n"
        f"⏳ ETA: {format_time(eta)}\n"
        f"⏱ Elapsed: {format_time(elapsed)}</b>"
    )


async def safe_edit(msg, text: str):
    """Edit a status message. Errors are logged, never crash the task."""
    try:
        await msg.edit_text(text, parse_mode=ParseMode.DISABLED)
    except MessageNotModified:
        pass
    except Exception as e:
        log.warning("Status edit failed: %s", e)


class Progress:
    """
    Progress callback for downloads (aiohttp) and uploads (Pyrogram).
    Pyrogram calls this from a worker thread, so each edit is scheduled
    onto the bot's main event loop.
    """

    def __init__(self, msg, action: str):
        self.msg = msg
        self.action = action
        self.start = time.time()
        self.last = 0.0
        self.loop = asyncio.get_running_loop()

    def __call__(self, current: int, total: int):
        now = time.time()
        if current != total and now - self.last < 3:
            return
        self.last = now

        text = progress_text(self.action, current, total, self.start)
        asyncio.run_coroutine_threadsafe(safe_edit(self.msg, text), self.loop)
