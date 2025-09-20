"""
EcoleHub Stage 2 Models - Extends Stage 1 with Messaging and Events
"""

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
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .db_types import UUIDType

# Import Stage 1 models
from .models_stage1 import Base, User


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    name = Column(String(200))
    type = Column(String(20), nullable=False)
    class_name = Column(String(10))  # For class-specific conversations
    created_by = Column(UUIDType(), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('direct', 'group', 'announcement', 'class')",
            name="valid_conversation_type",
        ),
        CheckConstraint(
            "class_name IS NULL OR class_name IN ('M1','M2','M3','P1','P2','P3','P4','P5','P6')",
            name="valid_class_name",
        ),
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    participants = relationship(
        "ConversationParticipant",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUIDType(), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(UUIDType(), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")
    edited_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('text', 'image', 'file', 'system')",
            name="valid_message_type",
        ),
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User")


class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    conversation_id = Column(
        UUIDType(), ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(
        UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_read_at = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User")


class Event(Base):
    __tablename__ = "events"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    location = Column(String(200))
    max_participants = Column(Integer)
    registration_required = Column(Boolean, default=False)
    registration_deadline = Column(DateTime(timezone=True))
    event_type = Column(String(50), default="general")
    class_name = Column(String(10))  # For class-specific events
    created_by = Column(UUIDType(), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('general', 'class', 'school', 'parent_meeting', 'activity', 'celebration')",
            name="valid_event_type",
        ),
        CheckConstraint(
            "class_name IS NULL OR class_name IN ('M1','M2','M3','P1','P2','P3','P4','P5','P6')",
            name="valid_event_class_name",
        ),
        CheckConstraint(
            "start_date < end_date OR end_date IS NULL", name="valid_event_dates"
        ),
        CheckConstraint(
            "max_participants IS NULL OR max_participants > 0",
            name="positive_max_participants",
        ),
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship(
        "EventParticipant", back_populates="event", cascade="all, delete-orphan"
    )


class EventParticipant(Base):
    __tablename__ = "event_participants"

    event_id = Column(
        UUIDType(), ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(
        UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="registered")
    notes = Column(Text)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('registered', 'attended', 'cancelled')",
            name="valid_participant_status",
        ),
    )

    # Relationships
    event = relationship("Event", back_populates="participants")
    user = relationship("User")


class UserStatus(Base):
    __tablename__ = "user_status"

    user_id = Column(
        UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    status_message = Column(String(100))
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User")


# Extend User model with Stage 2 relationships
User.conversations_created = relationship(
    "Conversation", foreign_keys="Conversation.created_by", back_populates="creator"
)
User.conversation_participations = relationship(
    "ConversationParticipant", back_populates="user"
)
User.messages = relationship("Message", back_populates="user")
User.events_created = relationship(
    "Event", foreign_keys="Event.created_by", back_populates="creator"
)
User.event_participations = relationship("EventParticipant", back_populates="user")
User.status = relationship("UserStatus", uselist=False, back_populates="user")
