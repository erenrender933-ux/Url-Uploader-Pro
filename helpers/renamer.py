import os
import re

import aiohttp

DEFAULT_FORMAT = "{title} S{season}E{episode} [{quality}]"
ANILIST_URL = "https://graphql.anilist.co"

# Brackets like [SubsPlease], (WEB), {tag}
BRACKETS = re.compile(r"\[[^\]]*\]|\([^)]*\)|\{[^}]*\}")

# Release tags that are not part of the anime name
TAGS = re.compile(
    r"\b(x26[45]|h\.?26[45]|hevc|avc|aac|ac3|flac|opus|10bit|8bit|"
    r"web[-_. ]?dl|webrip|bluray|bdrip|hdtv|dual[-_. ]?audio|multi|"
    r"english|tamil|hindi|telugu|malayalam|bengali|japanese|subs?|dub|e[-_. ]?subs?)\b",
    re.I,
)
RESOLUTION = re.compile(r"\b(2160|1080|720|480)p\b", re.I)
SE_MARKER = re.compile(r"\bS(\d{1,2})\s*E(\d{1,4})\b", re.I)
EP_MARKER = re.compile(r"\b(?:EP|Episode)[\s._-]*(\d{1,4})\b", re.I)
DASH_MARKER = re.compile(r"\s-\s*(\d{1,4})(?:v\d)?\b")


def parse_name(file_name: str) -> dict:
    """Pull title, season, episode and quality out of a messy file name."""
    base = os.path.splitext(file_name)[0]

    quality_match = RESOLUTION.search(base)
    quality = f"{quality_match.group(1)}p" if quality_match else "Unknown"

    season, episode = "01", "00"
    marker_pos = len(base)

    se = SE_MARKER.search(base)
    ep = EP_MARKER.search(base) or DASH_MARKER.search(base)

    if se:
        season, episode = se.group(1), se.group(2)
        marker_pos = se.start()
    elif ep:
        episode = ep.group(1)
        marker_pos = ep.start()

    # Title is everything before the season/episode marker
    title = _clean_title(base[:marker_pos])

    # Still empty? Try the whole name without brackets and tags
    if not title:
        title = _clean_title(base)

    return {
        "title": title or "Unknown",
        "season": season.zfill(2),
        "episode": episode.zfill(2),
