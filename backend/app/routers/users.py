from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, delete, select

from app.db.database import get_session
from app.db.models import User, UserProgress

router = APIRouter(prefix="/v1", tags=["users"])


class UserResponse(BaseModel):
    user_id: str
    name: str


class CreateUserRequest(BaseModel):
    user_id: str
    name: str = ""


@router.get("/users", response_model=list[UserResponse])
def list_users(
    session: Session = Depends(get_session),
) -> list[UserResponse]:
    """List all registered users."""
    stmt = select(User).order_by(User.name)
    users = session.exec(stmt).all()
    return [UserResponse(user_id=u.user_id, name=u.name) for u in users]


@router.post("/users", response_model=UserResponse)
def create_user(
    req: CreateUserRequest,
    session: Session = Depends(get_session),
) -> UserResponse:
    """Create a new user (simple, no auth)."""
    # Check if user_id already exists
    existing = session.exec(select(User).where(User.user_id == req.user_id)).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"User '{req.user_id}' already exists")

    user = User(
        user_id=req.user_id,
        name=req.name,
        created_at=datetime.now(timezone.utc),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse(user_id=user.user_id, name=user.name)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
) -> dict:
    """Delete a user and all their progress."""
    user = session.exec(select(User).where(User.user_id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    # Delete user's progress first
    session.exec(delete(UserProgress).where(UserProgress.user_id == user_id))
    # Delete the user
    session.delete(user)
    session.commit()

    return {"deleted": user_id}
