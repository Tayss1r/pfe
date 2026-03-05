import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .database import Base
from sqlalchemy import Table, Column


user_role_table = Table(
    "user_role",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base):
    __tablename__ = "role"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # relationships
    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_role_table, back_populates="roles", lazy="noload"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=user_role_table, back_populates="users", lazy="selectin"
    )
    interventions: Mapped[List["Intervention"]] = relationship(
        "Intervention", back_populates="technician", lazy="noload"
    )

    def __init__(self, *args, **kwargs):
        # Accept 'password' kwarg in constructor to avoid TypeError from declarative ctor
        password = kwargs.pop("password", None)
        # Pass other kwargs to SQLAlchemy's constructor
        super().__init__(*args, **kwargs)
        # If a password was provided, use the property setter to hash/assign it
        if password is not None:
            # Note: this is synchronous CPU work only (hashing), no DB IO
            self.password = password

    # write-only password property to accept either raw password or already-hashed value
    @property
    def password(self) -> None:
        raise AttributeError("password is write-only")

    @password.setter
    def password(self, value: Optional[str]) -> None:
        if value is None:
            self.hashed_password = None  # type: ignore[assignment]
            return
        # If value looks like a bcrypt hash (starts with $2), assume it's already hashed
        if isinstance(value, str) and value.startswith("$2"):
            self.hashed_password = value
        else:
            # hash synchronously (passlib) - no DB IO
            self.hashed_password = hash_password(value)


class Client(Base):
    __tablename__ = "client"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # relationships
    equipment_list: Mapped[List["Equipment"]] = relationship(
        "Equipment", back_populates="client"
    )


class Manufacturer(Base):
    __tablename__ = "manufacturer"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    support_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    support_phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # relationships
    equipment_list: Mapped[List["Equipment"]] = relationship(
        "Equipment", back_populates="manufacturer"
    )


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    serial_number: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("client.id", ondelete="RESTRICT"), nullable=False
    )
    manufacturer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("manufacturer.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_equipment_serial_number", "serial_number"),
        Index("ix_equipment_brand", "brand"),
        Index("ix_equipment_model", "model"),
        Index("ix_equipment_type", "type"),
        Index("ix_equipment_client_id", "client_id"),
        Index("ix_equipment_manufacturer_id", "manufacturer_id"),
    )

    # relationships
    client: Mapped["Client"] = relationship("Client", back_populates="equipment_list")
    manufacturer: Mapped[Optional["Manufacturer"]] = relationship(
        "Manufacturer", back_populates="equipment_list"
    )
    interventions: Mapped[List["Intervention"]] = relationship(
        "Intervention", back_populates="equipment", cascade="all, delete-orphan"
    )
    technical_documents: Mapped[List["TechnicalDocument"]] = relationship(
        "TechnicalDocument", back_populates="equipment", cascade="all, delete-orphan"
    )
    spare_parts: Mapped[List["SparePart"]] = relationship(
        "SparePart", back_populates="equipment", cascade="all, delete-orphan"
    )


class TechnicalDocument(Base):
    __tablename__ = "technical_document"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[str] = mapped_column(
        SQLEnum("PDF", "VIDEO", "IMAGE", name="document_type_enum"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # relationships
    equipment: Mapped["Equipment"] = relationship(
        "Equipment", back_populates="technical_documents"
    )


class SparePart(Base):
    __tablename__ = "spare_part"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # relationships
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="spare_parts")


class Intervention(Base):
    __tablename__ = "intervention"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    equipment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    technician_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        SQLEnum("IN_PROGRESS", "COMPLETED", "NOT_REPAIRED", name="intervention_status_enum"),
        nullable=False,
        server_default="IN_PROGRESS",
    )
    diagnostic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actions_taken: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    signature_image_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # relationships
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="interventions")
    technician: Mapped["User"] = relationship("User", back_populates="interventions")
    attachments: Mapped[List["InterventionAttachment"]] = relationship(
        "InterventionAttachment", back_populates="intervention", cascade="all, delete-orphan"
    )
    email_logs: Mapped[List["EmailLog"]] = relationship(
        "EmailLog", back_populates="intervention", cascade="all, delete-orphan"
    )


class InterventionAttachment(Base):
    __tablename__ = "intervention_attachment"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    intervention_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intervention.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    attachment_type: Mapped[str] = mapped_column(
        SQLEnum("PHOTO", "TECH_DOC", name="attachment_type_enum"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # relationships
    intervention: Mapped["Intervention"] = relationship(
        "Intervention", back_populates="attachments"
    )


class EmailLog(Base):
    __tablename__ = "email_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    intervention_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intervention.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_type: Mapped[str] = mapped_column(
        SQLEnum("MANUFACTURER", "CLIENT", "COMPANY", name="recipient_type_enum"),
        nullable=False,
    )
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # relationships
    intervention: Mapped["Intervention"] = relationship(
        "Intervention", back_populates="email_logs"
    )
