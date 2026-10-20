import asyncio
import os
from urllib.parse import unquote

import aiohttp
import gdown

from config import DOWNLOAD_DIR, MAX_FILE_SIZE
from helpers.gdrive import gdrive_file_id, is_gdrive
from helpers.progress import Progress, safe_edit


async def download(url: str, status_msg) -> str:
    """Download a Google Drive or direct link. Returns the local file path."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    if is_gdrive(url):
        return await _download_gdrive(url, status_msg)
    return await _download_direct(url, status_msg)


async def _download_gdrive(url: str, status_msg) -> str:
    file_id = gdrive_file_id(url)
    if not file_id:
        raise ValueError("Invalid Google Drive link.")

    await safe_edit(status_msg, "**Downloading from Google Drive...**")

    # A trailing separator tells gdown to keep the original file name
    output = os.path.join(DOWNLOAD_DIR, "")
    path = await asyncio.to_thread(
        gdown.download, id=file_id, output=output, quiet=True
    )
    if not path:
        raise ValueError(
            "Google Drive download failed. Make sure the file is shared as 'Anyone with the link'."
        )

    if os.path.getsize(path) > MAX_FILE_SIZE:
        os.remove(path)
        raise ValueError("File is larger than 4 GB.")
    return path


async def _download_direct(url: str, status_msg) -> str:
    name = unquote(os.path.basename(url.split("?")[0].rstrip("/"))) or "file.bin"
    path = os.path.join(DOWNLOAD_DIR, name)
    progress = Progress(status_msg, "Downloading")

    timeout = aiohttp.ClientTimeout(total=None, sock_read=60)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise ValueError(f"Download failed, HTTP {resp.status}")

            total = int(resp.headers.get("Content-Length", 0))
            if total > MAX_FILE_SIZE:
                raise ValueError("File is larger than 4 GB.")

            done = 0
            with open(path, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 1024):
                    f.write(chunk)
                    done += len(chunk)
                    if done > MAX_FILE_SIZE:
                        raise ValueError("File is larger than 4 GB.")
                    progress(done, total)
    return path
