"""
Chat Router

Endpoints compartilhados para o sistema de chat entre instrutor e aluno.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.application.dtos.chat_dtos import (
    ConversationResponseDTO,
    MessageResponseDTO,
    SendMessageDTO,
)
from src.application.use_cases.chat.get_instructor_conversations_use_case import (
    GetInstructorConversationsUseCase,
)
from src.application.use_cases.chat.send_message_use_case import SendMessageUseCase
from src.interface.api.dependencies import (
    CurrentUser,
    MessageRepo,
    get_get_instructor_conversations_use_case,
    get_send_message_use_case,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/messages", response_model=MessageResponseDTO, status_code=status.HTTP_201_CREATED)
async def send_message(
    dto: SendMessageDTO,
    current_user: CurrentUser,
    use_case: Annotated[SendMessageUseCase, Depends(get_send_message_use_case)],
) -> MessageResponseDTO:
    """
    Envia uma nova mensagem para outro usuário.
    Valida agendamento ativo e filtra conteúdo impróprio.
    """
    return await use_case.execute(current_user.id, dto)


@router.get("/conversations", response_model=list[ConversationResponseDTO])
async def list_conversations(
    current_user: CurrentUser,
    use_case: Annotated[
        GetInstructorConversationsUseCase, Depends(get_get_instructor_conversations_use_case)
    ],
) -> list[ConversationResponseDTO]:
    """
    Lista as conversas do usuário logado.
    Se for instrutor, filtra apenas por alunos com agendamentos ativos.
    """
    # Como o use case atual é específico GetInstructorConversationsUseCase,
    # vamos garantir que apenas instrutores chamem por enquanto ou adaptar depois.
    # Para o escopo atual (Instrutor), está correto.
    return await use_case.execute(current_user.id)


@router.get("/messages/{other_user_id}", response_model=list[MessageResponseDTO])
async def list_messages(
    other_user_id: str,
    current_user: CurrentUser,
    message_repo: MessageRepo,
) -> list[MessageResponseDTO]:
    """
    Lista o histórico de mensagens entre o usuário logado e outro usuário.
    """
    from uuid import UUID

    messages = await message_repo.list_by_conversation(
        current_user.id, UUID(other_user_id), limit=100
    )
    
    return [
        MessageResponseDTO(
            id=m.id,
            sender_id=m.sender_id,
            receiver_id=m.receiver_id,
            content=m.content,
            timestamp=m.timestamp,
            is_read=m.is_read,
        )
        for m in messages
    ]
