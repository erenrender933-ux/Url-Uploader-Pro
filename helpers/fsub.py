import logging

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import FSUB_CHANNELS, OWNER_ID

log = logging.getLogger("fsub")

# Statuses that count as "joined"
JOINED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.OWNER,
}

FSUB_TEXT = (
    "To use this bot, please join the channels below first.\n\n"
    "After joining, tap 'I Joined'."
)


async def get_missing_channels(client: Client, user_id: int) -> list[tuple[str, str]]:
    """
    Return a list of (channel title, invite link) for every channel the user has not joined.
    An empty list means the user is allowed to use the bot.
    Raises an exception if the bot cannot check a channel (usually: bot is not admin there).
    """
    if not FSUB_CHANNELS or user_id == OWNER_ID:
        return []

    missing = []
    for channel in FSUB_CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in JOINED_STATUSES:
                continue
        except UserNotParticipant:
            pass  # user is not in the channel, so add it to the missing list
        except Exception as e:
            log.error("FSub check failed for %s: %s", channel, e)
            raise

        chat = await client.get_chat(channel)
        if chat.invite_link:
            link = chat.invite_link
        elif chat.username:
            link = f"https://t.me/{chat.username}"
        else:
            link = await client.export_chat_invite_link(chat.id)
        missing.append((chat.title, link))

    return missing


def fsub_keyboard(missing: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """Join buttons for each missing channel, plus the 'I Joined' check button."""
    rows = [[InlineKeyboardButton(f"Join {title}", url=link)] for title, link in missing]
    rows.append([InlineKeyboardButton("✅ I Joined", callback_data="fsub_check")])
    return InlineKeyboardMarkup(rows)
