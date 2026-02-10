"""
Get Instructor Conversations Use Case

Caso de uso para listar as conversas do instrutor, filtrando apenas alunos com agendamentos ativos.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from src.application.dtos.chat_dtos import ConversationResponseDTO, MessageResponseDTO
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.interfaces.message_repository import IMessageRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository


@dataclass
class GetInstructorConversationsUseCase:
    """
    Caso de uso para carregar a lista de conversas de um instrutor.

    Regras:
        1. Listar apenas alunos que tenham agendamentos PENDING, CONFIRMED ou RESCHEDULE_REQUESTED.
        2. Unificar os alunos (um card por aluno).
        3. Incluir a última mensagem de cada conversa.
    """

    scheduling_repository: ISchedulingRepository
    message_repository: IMessageRepository

    async def execute(self, instructor_id: UUID) -> list[ConversationResponseDTO]:
        """
        Busca as conversas do instrutor.
        """
        active_statuses = [
            SchedulingStatus.PENDING,
            SchedulingStatus.CONFIRMED,
            SchedulingStatus.RESCHEDULE_REQUESTED,
        ]

        # 1. Buscar agendamentos ativos
        schedulings = await self.scheduling_repository.list_by_instructor(
            instructor_id=instructor_id,
            status=active_statuses,
            limit=200 # Limite alto para garantir que pegamos todos os alunos recentes
        )

        # 2. Agrupar por aluno e extrair nomes + próxima aula
        # Como o repositório já traz student_name preenchido (se carregado via JoinedLoad)
        conversations_dict = {}
        for s in schedulings:
            if s.student_id not in conversations_dict:
                conversations_dict[s.student_id] = {
                    "id": s.student_id,
                    "name": s.student_name or f"Aluno {str(s.student_id)[:8]}",
                    "next_lesson_at": s.scheduled_datetime
                }
            else:
                # Atualizar para a aula mais próxima se encontrarmos uma anterior
                if s.scheduled_datetime < conversations_dict[s.student_id]["next_lesson_at"]:
                    conversations_dict[s.student_id]["next_lesson_at"] = s.scheduled_datetime

        # 3. Para cada aluno, buscar a última mensagem
        results = []
        for student_id, student_info in conversations_dict.items():
            last_msg = await self.message_repository.get_last_message_between(
                instructor_id, student_id
            )
            
            last_msg_dto = None
            if last_msg:
                last_msg_dto = MessageResponseDTO(
                    id=last_msg.id,
                    sender_id=last_msg.sender_id,
                    receiver_id=last_msg.receiver_id,
                    content=last_msg.content,
                    timestamp=last_msg.timestamp,
                    is_read=last_msg.is_read
                )

            # Contar mensagens não lidas enviadas pelo aluno para o instrutor
            unread_count = await self.message_repository.count_unread_for_user(
                receiver_id=instructor_id,
                sender_id=student_id
            )

            results.append(ConversationResponseDTO(
                student_id=student_id,
                student_name=student_info["name"],
                last_message=last_msg_dto,
                unread_count=unread_count,
                next_lesson_at=student_info["next_lesson_at"]
            ))

        # Ordenar por data da última mensagem (conversas mais recentes primeiro)
        results.sort(
            key=lambda x: x.last_message.timestamp if x.last_message else datetime.min.replace(tzinfo=timezone.utc),
            reverse=True
        )

        return results
