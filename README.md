# URL Uploader Bot

A Telegram bot that downloads files from Google Drive or direct links and uploads them to the chat.

## Features
- Google Drive and direct link downloads
- Progress bar for download and upload
- Renamer ON/OFF with a custom format
- Keep only audio track 1 or 2 (removes other audio, subtitles and streams)
- Custom metadata title
- Custom thumbnail
- Limit on how many tasks run at the same time

## Setup (local)
1. Install Python 3.11+ and ffmpeg.
2. Copy `.env.example` to `.env` and fill in the values.
3. Install the packages:
   pip install -r requirements.txt
4. Run the bot:
   python bot.py

## Deploy on a VPS with Docker
git clone https://github.com/<your-username>/UrlUploaderBot.git
cd UrlUploaderBot
cp .env.example .env      # then edit .env with your values
docker build -t url-uploader-bot .
docker run -d --name uploader --restart unless-stopped --env-file .env url-uploader-bot
docker logs -f uploader

## Commands
- /start, /settings
- /renameron, /renameroff
- /setformat {title} S{season}E{episode} [{quality}]
- /keepaudio 1, /keepaudio 2, /keepaudio off
- /metadata <title>
- /setthumb (reply to a photo), /delthumb
- /stats (owner only)
