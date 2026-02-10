"""
Get Student Conversations Use Case

Caso de uso para listar as conversas do aluno, filtrando apenas instrutores com agendamentos ativos.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.application.dtos.chat_dtos import MessageResponseDTO, StudentConversationResponseDTO
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.interfaces.message_repository import IMessageRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


@dataclass
class GetStudentConversationsUseCase:
    """
    Caso de uso para carregar a lista de conversas de um aluno.

    Regras:
        1. Listar apenas instrutores que tenham agendamentos PENDING, CONFIRMED ou RESCHEDULE_REQUESTED.
        2. Unificar os instrutores (um card por instrutor).
        3. Incluir a última mensagem e contagem de não-lidas de cada conversa.
    """

    scheduling_repository: ISchedulingRepository
    message_repository: IMessageRepository

    async def execute(self, student_id: UUID) -> list[StudentConversationResponseDTO]:
        """
        Busca as conversas do aluno.
        """
        active_statuses = [
            SchedulingStatus.PENDING,
            SchedulingStatus.CONFIRMED,
            SchedulingStatus.RESCHEDULE_REQUESTED,
        ]

        # 1. Buscar agendamentos ativos do aluno
        schedulings = await self.scheduling_repository.list_by_student(
            student_id=student_id,
            status=active_statuses,
            limit=200,
        )

        # 2. Agrupar por instrutor
        conversations_dict: dict = {}
        for s in schedulings:
            if s.instructor_id not in conversations_dict:
                conversations_dict[s.instructor_id] = {
                    "id": s.instructor_id,
                    "name": s.instructor_name or f"Instrutor {str(s.instructor_id)[:8]}",
                }

        # 3. Para cada instrutor, buscar última mensagem e contagem de não-lidas
        results = []
        for instructor_id, info in conversations_dict.items():
            last_msg = await self.message_repository.get_last_message_between(
                student_id, instructor_id
            )

            last_msg_dto = None
            if last_msg:
                last_msg_dto = MessageResponseDTO(
                    id=last_msg.id,
                    sender_id=last_msg.sender_id,
                    receiver_id=last_msg.receiver_id,
                    content=last_msg.content,
                    timestamp=last_msg.timestamp,
                    is_read=last_msg.is_read,
                )

            unread = await self.message_repository.count_unread_for_user(
                receiver_id=student_id,
                sender_id=instructor_id,
            )

            results.append(
                StudentConversationResponseDTO(
                    instructor_id=instructor_id,
                    instructor_name=info["name"],
                    last_message=last_msg_dto,
                    unread_count=unread,
                )
            )

        # Ordenar por última mensagem mais recente
        results.sort(
            key=lambda x: x.last_message.timestamp if x.last_message else datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )

        return results
