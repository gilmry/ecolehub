"""
EcoleHub Stage 2 - WebSocket Manager for Real-time Communication
"""

import json
from typing import Dict, List, Set
from uuid import UUID

import redis
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .models_stage2 import ConversationParticipant, Message, User, UserStatus


class WebSocketManager:
    """
    Manages WebSocket connections for real-time messaging.
    Uses Redis for scaling across multiple backend instances.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        # Active connections: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # User subscriptions: user_id -> Set[conversation_ids]
        self.user_subscriptions: Dict[str, Set[str]] = {}

        # Redis for pub/sub and presence
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

    async def connect(self, websocket: WebSocket, user_id: UUID, db: Session):
        """Connect user and mark as online."""
        await websocket.accept()

        user_id_str = str(user_id)
        self.active_connections[user_id_str] = websocket
        self.user_subscriptions[user_id_str] = set()

        # Mark user as online
        await self._update_user_status(user_id, True, db)

        # Subscribe to user's conversations
        await self._subscribe_user_conversations(user_id_str, db)

        print(f"👋 User {user_id_str} connected")

    async def disconnect(self, user_id: UUID, db: Session):
        """Disconnect user and mark as offline."""
        user_id_str = str(user_id)

        if user_id_str in self.active_connections:
            del self.active_connections[user_id_str]

        if user_id_str in self.user_subscriptions:
            del self.user_subscriptions[user_id_str]

        # Mark user as offline
        await self._update_user_status(user_id, False, db)

        print(f"👋 User {user_id_str} disconnected")

    async def send_personal_message(self, message: str, user_id: UUID):
        """Send message to specific user."""
        user_id_str = str(user_id)

        if user_id_str in self.active_connections:
            try:
                await self.active_connections[user_id_str].send_text(message)
                return True
            except BaseException:
                # Connection closed, clean up
                del self.active_connections[user_id_str]
                return False
        return False

    async def broadcast_to_conversation(
        self, conversation_id: UUID, message_data: dict, sender_id: UUID = None
    ):
        """Broadcast message to all participants in a conversation."""
        conversation_id_str = str(conversation_id)
        sender_id_str = str(sender_id) if sender_id else None

        message_json = json.dumps(message_data)

        # Send to all connected users subscribed to this conversation
        disconnected_users = []

        for user_id_str, subscriptions in self.user_subscriptions.items():
            if conversation_id_str in subscriptions and user_id_str != sender_id_str:
                if user_id_str in self.active_connections:
                    try:
                        await self.active_connections[user_id_str].send_text(
                            message_json
                        )
                    except BaseException:
                        disconnected_users.append(user_id_str)

        # Clean up disconnected users
        for user_id_str in disconnected_users:
            if user_id_str in self.active_connections:
                del self.active_connections[user_id_str]
            if user_id_str in self.user_subscriptions:
                del self.user_subscriptions[user_id_str]

    async def handle_message(self, websocket: WebSocket, user_id: UUID, db: Session):
        """Handle incoming WebSocket messages."""
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)

                message_type = message_data.get("type")

                if message_type == "send_message":
                    await self._handle_send_message(user_id, message_data, db)
                elif message_type == "join_conversation":
                    await self._handle_join_conversation(user_id, message_data, db)
                elif message_type == "leave_conversation":
                    await self._handle_leave_conversation(user_id, message_data, db)
                elif message_type == "typing":
                    await self._handle_typing(user_id, message_data)
                elif message_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

        except WebSocketDisconnect:
            await self.disconnect(user_id, db)
        except Exception as e:
            print(f"❌ WebSocket error for user {user_id}: {e}")
            await self.disconnect(user_id, db)

    async def _handle_send_message(
        self, user_id: UUID, message_data: dict, db: Session
    ):
        """Handle sending a message to a conversation."""
        conversation_id = UUID(message_data.get("conversation_id"))
        content = message_data.get("content", "").strip()

        if not content:
            return

        # Verify user is participant
        participant = (
            db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
            )
            .first()
        )

        if not participant:
            return

        # Create message in database
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            content=content,
            message_type="text",
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        # Get user info for broadcast
        user = db.query(User).filter(User.id == user_id).first()

        # Broadcast to conversation participants
        broadcast_data = {
            "type": "new_message",
            "message": {
                "id": str(message.id),
                "conversation_id": str(conversation_id),
                "user_id": str(user_id),
                "user_name": f"{user.first_name} {user.last_name}",
                "content": content,
                "created_at": message.created_at.isoformat(),
            },
        }

        await self.broadcast_to_conversation(conversation_id, broadcast_data, user_id)

    async def _handle_join_conversation(
        self, user_id: UUID, message_data: dict, db: Session
    ):
        """Handle user joining a conversation."""
        conversation_id = UUID(message_data.get("conversation_id"))
        user_id_str = str(user_id)
        conversation_id_str = str(conversation_id)

        # Add to user's subscriptions
        if user_id_str not in self.user_subscriptions:
            self.user_subscriptions[user_id_str] = set()

        self.user_subscriptions[user_id_str].add(conversation_id_str)

        # Update last_read_at
        participant = (
            db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id,
            )
            .first()
        )

        if participant:
            participant.last_read_at = func.now()
            db.commit()

    async def _handle_leave_conversation(
        self, user_id: UUID, message_data: dict, db: Session
    ):
        """Handle user leaving a conversation."""
        conversation_id_str = str(message_data.get("conversation_id"))
        user_id_str = str(user_id)

        if user_id_str in self.user_subscriptions:
            self.user_subscriptions[user_id_str].discard(conversation_id_str)

    async def _handle_typing(self, user_id: UUID, message_data: dict):
        """Handle typing indicators."""
        conversation_id = UUID(message_data.get("conversation_id"))
        is_typing = message_data.get("is_typing", False)

        # Get user info
        user_id_str = str(user_id)

        # Broadcast typing status
        typing_data = {
            "type": "typing",
            "conversation_id": str(conversation_id),
            "user_id": user_id_str,
            "is_typing": is_typing,
        }

        await self.broadcast_to_conversation(conversation_id, typing_data, user_id)

    async def _subscribe_user_conversations(self, user_id_str: str, db: Session):
        """Subscribe user to their conversations."""
        user_id = UUID(user_id_str)

        # Get user's conversation participations
        participations = (
            db.query(ConversationParticipant)
            .filter(ConversationParticipant.user_id == user_id)
            .all()
        )

        for participation in participations:
            conversation_id_str = str(participation.conversation_id)
            self.user_subscriptions[user_id_str].add(conversation_id_str)

    async def _update_user_status(self, user_id: UUID, is_online: bool, db: Session):
        """Update user online status."""
        user_status = db.query(UserStatus).filter(UserStatus.user_id == user_id).first()

        if not user_status:
            user_status = UserStatus(
                user_id=user_id, is_online=is_online, last_seen=func.now()
            )
            db.add(user_status)
        else:
            user_status.is_online = is_online
            user_status.last_seen = func.now()

        db.commit()

    def get_online_users(self) -> List[str]:
        """Get list of currently online user IDs."""
        return list(self.active_connections.keys())

    def is_user_online(self, user_id: UUID) -> bool:
        """Check if user is currently online."""
        return str(user_id) in self.active_connections


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
