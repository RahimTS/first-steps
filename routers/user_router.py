from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from loguru import logger

from repositories.user_repository import UserRepository
from models.user import UserCreate, UserOut


router = APIRouter(prefix="/users", tags=["users"])


def get_user_repository(request: Request):
    db = request.app.mongo_db
    return UserRepository(db)


@router.post("/", response_model=UserOut, summary="Create a new user")
async def create_user(payload: UserCreate, repo=Depends(get_user_repository)) -> UserOut:
    logger.debug(f"Create user called with: {payload.model_dump(mode='json')}")
    created = await repo.add_user(payload)
    return created


@router.get("/{user_id}", response_model=UserOut, summary="Get a user by id")
async def get_user(user_id: str, repo=Depends(get_user_repository)) -> UserOut:
    logger.debug(f"Get user called with id={user_id}")
    user = await repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
