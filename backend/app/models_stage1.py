import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .db_types import UUIDType

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    # GDPR/consent metadata
    consent_version = Column(String(20))
    consented_at = Column(DateTime(timezone=True))
    privacy_locale = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    children = relationship(
        "Child", back_populates="parent", cascade="all, delete-orphan"
    )
    sel_services = relationship(
        "SELService", back_populates="user", cascade="all, delete-orphan"
    )
    transactions_sent = relationship(
        "SELTransaction",
        foreign_keys="SELTransaction.from_user_id",
        back_populates="from_user",
    )
    transactions_received = relationship(
        "SELTransaction",
        foreign_keys="SELTransaction.to_user_id",
        back_populates="to_user",
    )
    sel_balance = relationship(
        "SELBalance", uselist=False, back_populates="user", cascade="all, delete-orphan"
    )


class Child(Base):
    __tablename__ = "children"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    parent_id = Column(
        UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    first_name = Column(String(100), nullable=False)
    class_name = Column(String(10), nullable=False)
    birth_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "class_name IN ('M1','M2','M3','P1','P2','P3','P4','P5','P6')",
            name="valid_class_name",
        ),
    )

    # Relationships
    parent = relationship("User", back_populates="children")


class SELCategory(Base):
    __tablename__ = "sel_categories"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SELService(Base):
    __tablename__ = "sel_services"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    units_per_hour = Column(Integer, default=60)  # 60 units = 1 hour standard
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="sel_services")
    transactions = relationship("SELTransaction", back_populates="service")


class SELTransaction(Base):
    __tablename__ = "sel_transactions"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    from_user_id = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    to_user_id = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    service_id = Column(UUIDType(), ForeignKey("sel_services.id"))
    units = Column(Integer, nullable=False)
    description = Column(Text)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("units > 0", name="positive_units"),
        CheckConstraint(
            "status IN ('pending', 'approved', 'completed', 'cancelled')",
            name="valid_status",
        ),
    )

    # Relationships
    from_user = relationship(
        "User", foreign_keys=[from_user_id], back_populates="transactions_sent"
    )
    to_user = relationship(
        "User", foreign_keys=[to_user_id], back_populates="transactions_received"
    )
    service = relationship("SELService", back_populates="transactions")


class SELBalance(Base):
    __tablename__ = "sel_balances"

    user_id = Column(
        UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    balance = Column(Integer, default=120)  # Initial: 120 units (2 hours credit)
    total_given = Column(Integer, default=0)
    total_received = Column(Integer, default=0)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Constraints - Belgian SEL limits
    __table_args__ = (
        CheckConstraint("balance >= -300 AND balance <= 600", name="balance_limits"),
        CheckConstraint("total_given >= 0", name="positive_total_given"),
        CheckConstraint("total_received >= 0", name="positive_total_received"),
    )

    # Relationships
    user = relationship("User", back_populates="sel_balance")
