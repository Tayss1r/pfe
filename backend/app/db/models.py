from datetime import datetime, date as dt_date, time as dt_time
from typing import Literal
from .database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import TIMESTAMP, text, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SQLEnum

class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    fullname: Mapped[str] = mapped_column(nullable=False)
    is_verified: Mapped[bool] = mapped_column(server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )
    role: Mapped[Literal["technicien", "admin"]] = mapped_column(
        SQLEnum("technicien", "admin", name="user_roles"),
        nullable=False,
        server_default="technicien"
    )