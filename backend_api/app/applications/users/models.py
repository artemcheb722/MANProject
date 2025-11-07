import uuid
from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List, Dict
from database.base_models import Base
from sqlalchemy.ext.mutable import MutableList


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    uuid_data: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)

    name: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]

    is_admin: Mapped[bool] = mapped_column(default=False, nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=True)
    profile_description: Mapped[str] = mapped_column(Text, nullable=True)
    user_avatar: Mapped[str] = mapped_column(nullable=True)
    followers: Mapped[int] = mapped_column(default=0)
    subscriptions: Mapped[int] = mapped_column(default=0)

    comments: Mapped[List[Dict]] = mapped_column(MutableList.as_mutable(JSON),default=list,nullable=True)

    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan"
    )



