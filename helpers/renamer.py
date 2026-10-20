import os
import re

DEFAULT_FORMAT = "{title} S{season}E{episode} [{quality}]"


def parse_name(file_name: str) -> dict:
    """Pull title, season, episode and quality out of a messy file name."""
    base = os.path.splitext(file_name)[0]
    season, episode = "01", "00"

    se = re.search(r"S(\d{1,2})\s*E(\d{1,3})", base, re.I)
    if se:
        season, episode = se.group(1), se.group(2)
    else:
        ep = re.search(r"(?:\bEP?|Episode)[\s._-]*(\d{1,3})\b", base, re.I) or \
             re.search(r"[\s._-](\d{1,3})(?=[\s._-]|$)", base)
        if ep:
            episode = ep.group(1)

    # Everything before the first season/episode marker or bracket is the title
    cut = re.split(
        r"S\d{1,2}\s*E\d|\bE(?:P|pisode)?[\s._-]*\d|\[|\(",
        base,
        maxsplit=1,
        flags=re.I,
    )[0]
    title = re.sub(r"[._]+", " ", cut).strip(" -")

    q = re.search(r"(2160|1080|720|480)p", base, re.I)
    quality = f"{q.group(1)}p" if q else "Unknown"

    return {
        "title": title or "Unknown",
        "season": season.zfill(2),
        "episode": episode.zfill(2),
        "quality": quality,
    }


def build_name(fmt: str, original_name: str) -> str:
    """Apply the user's format to a file name and keep the original extension."""
    info = parse_name(original_name)
    ext = os.path.splitext(original_name)[1]
    try:
        name = fmt.format(**info)
    except (KeyError, IndexError, ValueError):
        name = DEFAULT_FORMAT.format(**info)
    return name.strip().replace("/", "-") + ext
