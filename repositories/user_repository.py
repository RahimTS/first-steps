from __future__ import annotations

from typing import Optional
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
from datetime import datetime

from models.user import UserCreate, UserDB, UserOut
from utils.collections import Collections


class UserRepository:
    """Repository responsible for user persistence and retrieval.

    This class encapsulates all DB access for users. It ensures:
    - `user_index` is assigned as an auto-incrementing integer.
    - Enforces uniqueness on `id` (create unique index on first use).
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._users = db.get_collection(Collections.USERS.value)
        self._counters = db.get_collection(Collections.COUNTERS.value)
        self._initialized = False

    async def _initialize(self) -> None:
        if self._initialized:
            return
        # Ensure unique index on id and user_index
        await self._users.create_index("id", unique=True, name="uniq_id")
        await self._users.create_index("user_index", unique=True, name="uniq_user_index")
        self._initialized = True
        logger.info("UserRepository initialized: indexes ensured")

    async def _get_next_user_index(self) -> int:
        """Atomically increment and return the next user index using a counters collection."""
        result = await self._counters.find_one_and_update(
            {"_id": "user_index"},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        seq = result.get("seq", 1) if result else 1
        if seq == 1:
            # First initialization: set to 1 explicitly
            await self._counters.update_one({"_id": "user_index"}, {"$set": {"seq": 1}}, upsert=True)
        return int(seq)

    async def add_user(self, payload: UserCreate) -> UserOut:
        await self._initialize()
        user_db = UserDB(**payload.model_dump())
        user_db.user_index = await self._get_next_user_index()
        document = user_db.model_dump()

        try:
            await self._users.insert_one(document)
        except DuplicateKeyError:
            # Very rare: id collision; regenerate and retry once
            from models.user import generate_short_hex_id

            user_db.id = generate_short_hex_id()
            document = user_db.model_dump()
            await self._users.insert_one(document)

        logger.info(f"Inserted user id={user_db.id} user_index={user_db.user_index}")
        return UserOut(**user_db.model_dump())

    async def get_user_by_id(self, user_id: str) -> Optional[UserOut]:
        await self._initialize()
        doc = await self._users.find_one({"id": user_id}, {"_id": 0})
        if not doc:
            logger.info(f"User not found for id={user_id}")
            return None
        return UserOut(**doc)
