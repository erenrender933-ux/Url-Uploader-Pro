import asyncio
import json


async def _run(cmd: list[str]):
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(err.decode(errors="ignore")[-300:])


async def count_audio_tracks(path: str) -> int:
    proc = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "quiet",
        "-select_streams", "a",
        "-show_entries", "stream=index",
        "-of", "json",
        path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, _ = await proc.communicate()
    return len(json.loads(out or b"{}").get("streams", []))


async def process_file(
    src: str,
    dst: str,
    audio_track: int | None = None,
    title: str | None = None,
):
    """
    audio_track: 1 or 2 keeps only that audio track and removes all other
                 audio, subtitles and streams. None keeps everything.
    title: sets the title metadata. None leaves it unchanged.
    """
    cmd = ["ffmpeg", "-y", "-i", src]

    if audio_track is None:
        cmd += ["-map", "0"]
    else:
        total = await count_audio_tracks(src)
        if audio_track > total:
            raise ValueError(
                f"This file has only {total} audio track(s), so track {audio_track} can't be kept."
            )
        # 0:v? = video if present, 0:a:N = the chosen audio track (N starts at 0)
        cmd += ["-map", "0:v?", "-map", f"0:a:{audio_track - 1}"]

    cmd += ["-c", "copy"]

    if title:
        cmd += ["-metadata", f"title={title}"]

    cmd.append(dst)
    await _run(cmd)
