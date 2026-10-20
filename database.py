from motor.motor_asyncio import AsyncIOMotorClient

from config import DB_URI, DB_NAME

client = AsyncIOMotorClient(DB_URI)
db = client[DB_NAME]
users = db["users"]


async def add_user(user_id: int, name: str):
    """Create a user record the first time they talk to the bot."""
    await users.update_one(
        {"_id": user_id},
        {"$setOnInsert": {"name": name, "settings": {}}},
        upsert=True,
    )


async def get_settings(user_id: int) -> dict:
    user = await users.find_one({"_id": user_id})
    return (user or {}).get("settings", {})


async def update_setting(user_id: int, key: str, value):
    await users.update_one(
        {"_id": user_id},
        {"$set": {f"settings.{key}": value}},
        upsert=True,
    )


async def total_users() -> int:
    return await users.count_documents({})
