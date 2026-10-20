import os

from PIL import Image

MAX_THUMB_BYTES = 200 * 1024  # Telegram limit for thumbnails


def prepare_thumb(src: str, dst: str) -> str:
    """Convert any image to a JPEG that Telegram accepts as a thumbnail."""
    with Image.open(src) as img:
        img = img.convert("RGB")
        img.thumbnail((320, 320))  # Telegram limit: max 320px on each side

    quality = 90
    while True:
        img.save(dst, "JPEG", quality=quality)
        if os.path.getsize(dst) <= MAX_THUMB_BYTES or quality <= 40:
            break
        quality -= 10
    return dst
