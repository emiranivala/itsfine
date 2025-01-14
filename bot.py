import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from database.db import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "bot_session",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN
        )

    async def start(self):
        await super().start()
        logging.info("Bot started!")
        try:
            total_users = await db.total_users_count()
            logging.info(f"Total users: {total_users}")
        except Exception as e:
            logging.error(f"Error accessing database: {e}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped.")

if __name__ == "__main__":
    Bot().run()
