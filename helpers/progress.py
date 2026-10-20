import asyncio
import time

from pyrogram.errors import MessageNotModified


def human_size(n: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} TB"


def progress_text(action: str, current: int, total: int, start: float) -> str:
    elapsed = max(time.time() - start, 0.1)
    speed = current / elapsed
    percent = current * 100 / total if total else 0
    filled = min(int(percent // 10), 10)
    bar = "■" * filled + "□" * (10 - filled)
    eta = (total - current) / speed if speed and total else 0
    return (
        f"**{action}**\n"
        f"[{bar}] {percent:.1f}%\n"
        f"Done: {human_size(current)} / {human_size(total)}\n"
        f"Speed: {human_size(speed)}/s\n"
        f"ETA: {int(eta)}s"
    )


async def safe_edit(msg, text: str):
    """Edit a message but never crash if Telegram rejects the edit."""
    try:
        await msg.edit_text(text)
    except MessageNotModified:
        pass
    except Exception:
        pass


class Progress:
    """
    Progress callback for downloads (aiohttp) and uploads (Pyrogram).
    Pyrogram can call this from a worker thread, so every edit is
    handed back to the bot's main event loop.
    """

    def __init__(self, msg, action: str):
        self.msg = msg
        self.action = action
        self.start = time.time()
        self.last = 0.0
        # Created inside an async handler, so a running loop always exists here
        self.loop = asyncio.get_running_loop()

    def __call__(self, current: int, total: int):
        now = time.time()
        if current != total and now - self.last < 3:
            return
        self.last = now

        text = progress_text(self.action, current, total, self.start)
        asyncio.run_coroutine_threadsafe(safe_edit(self.msg, text), self.loop)
