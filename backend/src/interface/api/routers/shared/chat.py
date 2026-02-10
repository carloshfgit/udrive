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
    StudentConversationResponseDTO,
    UnreadCountResponseDTO,
)
from src.application.dtos.scheduling_dtos import SchedulingResponseDTO
from src.application.use_cases.chat.get_instructor_conversations_use_case import (
    GetInstructorConversationsUseCase,
)
from src.application.use_cases.chat.get_student_conversations_use_case import (
    GetStudentConversationsUseCase,
)
from src.application.use_cases.chat.get_instructor_lessons_for_student_use_case import (
    GetInstructorLessonsForStudentUseCase,
)
from src.application.use_cases.chat.send_message_use_case import SendMessageUseCase
from src.interface.api.dependencies import (
    CurrentUser,
    MessageRepo,
    get_db,
    get_get_instructor_conversations_use_case,
    get_get_student_conversations_use_case,
    get_get_instructor_lessons_for_student_use_case,
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


@router.get("/conversations/student", response_model=list[StudentConversationResponseDTO])
async def list_student_conversations(
    current_user: CurrentUser,
    use_case: Annotated[
        GetStudentConversationsUseCase, Depends(get_get_student_conversations_use_case)
    ],
) -> list[StudentConversationResponseDTO]:
    """
    Lista as conversas do aluno logado com seus instrutores.
    Filtra apenas instrutores com agendamentos ativos.
    """
    return await use_case.execute(current_user.id)


@router.get("/unread-count", response_model=UnreadCountResponseDTO)
async def get_unread_count(
    current_user: CurrentUser,
    message_repo: MessageRepo,
) -> UnreadCountResponseDTO:
    """
    Retorna a contagem total de mensagens não lidas do usuário logado.
    """
    count = await message_repo.count_total_unread(current_user.id)
    return UnreadCountResponseDTO(unread_count=count)


@router.get("/messages/{other_user_id}", response_model=list[MessageResponseDTO])
async def list_messages(
    other_user_id: str,
    current_user: CurrentUser,
    message_repo: MessageRepo,
    db_session: Annotated["AsyncSession", Depends(get_db)],
) -> list[MessageResponseDTO]:
    """
    Lista o histórico de mensagens entre o usuário logado e outro usuário.
    Marca automaticamente as mensagens não lidas como lidas.
    """
    from uuid import UUID

    messages = await message_repo.list_by_conversation(
        current_user.id, UUID(other_user_id), limit=100
    )
    
    # Marcar mensagens não lidas como lidas
    unread_message_ids = [m.id for m in messages if not m.is_read and m.receiver_id == current_user.id]
    if unread_message_ids:
        await message_repo.mark_as_read(unread_message_ids)
        # Commit explícito necessário pois GET não faz auto-commit
        await db_session.commit()
    
    return [
        MessageResponseDTO(
            id=m.id,
            sender_id=m.sender_id,
            receiver_id=m.receiver_id,
            content=m.content,
            timestamp=m.timestamp,
            is_read=m.is_read or m.receiver_id == current_user.id,  # Retornar como lida se foi marcada agora
        )
        for m in messages
    ]


@router.get("/lessons/instructor/{instructor_id}", response_model=list[SchedulingResponseDTO])
async def get_lessons_with_instructor(
    instructor_id: str,
    current_user: CurrentUser,
    use_case: Annotated[
        GetInstructorLessonsForStudentUseCase, Depends(get_get_instructor_lessons_for_student_use_case)
    ],
) -> list[SchedulingResponseDTO]:
    """
    Lista o histórico de aulas do aluno logado com um instrutor específico.
    Usado quando o aluno clica em "Ver Aulas" no chat.
    """
    from uuid import UUID
    
    return await use_case.execute(
        student_id=current_user.id,
        instructor_id=UUID(instructor_id)
    )

