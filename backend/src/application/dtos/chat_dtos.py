"""
Chat DTOs

Definição de Data Transfer Objects para o sistema de chat.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SendMessageDTO(BaseModel):
    """DTO para envio de mensagem."""
    receiver_id: UUID
    content: str = Field(..., min_length=1, max_length=2000)


class MessageResponseDTO(BaseModel):
    """DTO para resposta de mensagem individual."""
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    content: str
    timestamp: datetime
    is_read: bool


class ConversationResponseDTO(BaseModel):
    """DTO para um card de conversa na lista."""
    student_id: UUID
    student_name: str
    last_message: MessageResponseDTO | None = None
    unread_count: int = 0
