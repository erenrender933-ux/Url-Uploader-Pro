import re

URL_PATTERN = re.compile(r"^https?://\S+$")


def is_url(text: str) -> bool:
    return bool(URL_PATTERN.match(text.strip()))


def is_gdrive(url: str) -> bool:
    return "drive.google.com" in url or "docs.google.com" in url


def gdrive_file_id(url: str) -> str | None:
    # Supports /file/d/<id>/view and ?id=<id> formats
    match = re.search(r"/d/([\w-]+)", url) or re.search(r"[?&]id=([\w-]+)", url)
    return match.group(1) if match else None
