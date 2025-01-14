import os
import asyncio
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import UsernameNotOccupied
from config import API_ID, API_HASH, BOT_TOKEN, ERROR_MESSAGE
from utils import db, batch_temp
from utils.file_splitter import split_large_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Status updater
async def status_updater(client, statusfile, message, chat, prefix):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r") as file:
                txt = file.read().strip()
            await client.edit_message_text(chat, message.id, f"**{prefix}:** **{txt}**")
            await asyncio.sleep(10)
        except Exception as e:
            logging.error(f"Error updating {prefix} status: {e}")
            await asyncio.sleep(5)

# Progress writer
def write_progress(current, total, message, file_prefix):
    with open(f"{message.id}{file_prefix}status.txt", "w") as f:
        f.write(f"{current * 100 / total:.1f}%")

# Command: /start
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    buttons = [
        [InlineKeyboardButton("❣️ Developer", url="https://t.me/She_who_remain")],
        [
            InlineKeyboardButton("🔍 Support Group", url="https://t.me/+r2f3gdPKnI9jMDg0"),
            InlineKeyboardButton("🤖 Update Channel", url="https://t.me/+r2f3gdPKnI9jMDg0")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id,
        text=(
            f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot. "
            "I can help you download restricted content from Telegram posts. "
            "Use /login to get started and /help for more details.</b>"
        ),
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )

# Command: /help
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    help_text = (
        "To download restricted content:\n"
        "- Use /login to authenticate.\n"
        "- Send the link of the restricted content.\n"
        "- Use /cancel to stop an ongoing batch.\n\n"
        "Note: Ensure your session is valid and active."
    )
    await client.send_message(chat_id=message.chat.id, text=help_text)

# Command: /cancel
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="**Batch Successfully Cancelled.**")

# Handle restricted content
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        if not batch_temp.IS_BATCH.get(message.from_user.id, True):
            return await message.reply_text("**Another task is processing. Use /cancel to stop it before starting a new one.**")

        # Parse message text
        data = message.text.split("/")
        temp = data[-1].replace("?single", "").split("-")
        from_id = int(temp[0].strip())
        to_id = int(temp[1].strip()) if len(temp) > 1 else from_id

        batch_temp.IS_BATCH[message.from_user.id] = False
        for msg_id in range(from_id, to_id + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**Please /login to download restricted content.**")
                batch_temp.IS_BATCH[message.from_user.id] = True
                return

            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
            except Exception:
                batch_temp.IS_BATCH[message.from_user.id] = True
                return await message.reply("**Session expired. Please /logout and then /login again.**")

            try:
                await process_restricted_content(client, acc, message, data, msg_id)
            except Exception as e:
                if ERROR_MESSAGE:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            await asyncio.sleep(3)

        batch_temp.IS_BATCH[message.from_user.id] = True

# Handle restricted content processing
async def process_restricted_content(client, acc, message, data, msg_id):
    if "https://t.me/c/" in message.text:
        chat_id = int("-100" + data[4])
    elif "https://t.me/b/" in message.text:
        chat_id = data[4]
    else:
        chat_id = data[3]

    msg = await acc.get_messages(chat_id, msg_id)
    if not msg or msg.empty:
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    if msg_type == "Text":
        await client.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        return

    smsg = await client.send_message(message.chat.id, "**Downloading...**", reply_to_message_id=message.id)
    asyncio.create_task(status_updater(client, f"{message.id}downstatus.txt", smsg, message.chat.id, "Downloaded"))

    try:
        file = await acc.download_media(msg, progress=write_progress, progress_args=[message, "down"])
        os.remove(f"{message.id}downstatus.txt")
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        return await smsg.delete()

    await upload_file(client, file, message, smsg)

# Upload file
async def upload_file(client, file, message, smsg):
    if os.path.getsize(file) > 2 * 1024 * 1024 * 1024:
        chunks = split_large_file(file, 2 * 1024 * 1024 * 1024)
        for chunk in chunks:
            await client.send_document(message.chat.id, chunk, reply_to_message_id=message.id)
            os.remove(chunk)
    else:
        await client.send_document(message.chat.id, file, reply_to_message_id=message.id)

    os.remove(file)
    await smsg.delete()

# Determine message type
def get_message_type(msg):
    if msg.document: return "Document"
    if msg.video: return "Video"
    if msg.photo: return "Photo"
    if msg.text: return "Text"
    return None
