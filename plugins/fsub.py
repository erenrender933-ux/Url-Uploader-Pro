from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery

from helpers.fsub import fsub_keyboard, get_missing_channels


@Client.on_callback_query(filters.regex("^fsub_check$"))
async def fsub_check_callback(client: Client, query: CallbackQuery):
    try:
        missing = await get_missing_channels(client, query.from_user.id)
    except Exception:
        return await query.answer(
            "Bot config error. Please contact the owner.", show_alert=True
        )

    if missing:
        await query.answer("You have not joined all channels yet.", show_alert=True)
        try:
            await query.message.edit_reply_markup(fsub_keyboard(missing))
        except MessageNotModified:
            pass
        return

    await query.answer("Verified!")
    try:
        await query.message.edit_text(
            "✅ Verified! Now send me a Google Drive or direct link."
        )
    except MessageNotModified:
        pass
