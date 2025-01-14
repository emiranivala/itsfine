from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from database.db import db  # Use your MongoDB-based Database class

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
        print("Bot started!")
        print(f"Total users: {await db.total_users_count()}")  # Example usage of your Database

    async def stop(self, *args):
        await super().stop()
        print("Bot stopped.")

if __name__ == "__main__":
    Bot().run()
