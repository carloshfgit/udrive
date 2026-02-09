"""
Send Message Use Case

Caso de uso para enviar mensagens de chat com validação de agendamento ativo e filtro de conteúdo.
"""

import re
from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.chat_dtos import MessageResponseDTO, SendMessageDTO
from src.domain.entities.message import Message
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.exceptions import (
    ActiveSchedulingRequiredException,
    ForbiddenContentException,
    UserNotFoundException,
)
from src.domain.interfaces.message_repository import IMessageRepository
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class SendMessageUseCase:
    """
    Caso de uso para enviar mensagens de chat.

    Regras:
        1. Validar se remetente e destinatário existem.
        2. Validar se existe agendamento ativo entre as partes.
        3. Filtrar conteúdo da mensagem para evitar desvios da plataforma.
        4. Salvar e retornar a mensagem.
    """

    message_repository: IMessageRepository
    scheduling_repository: ISchedulingRepository
    user_repository: IUserRepository

    # Padrões proibidos (padrão regex)
    PROHIBITED_PATTERNS = [
        r"[\w\.-]+@[\w\.-]+\.\w+",  # Emails
        r"\b\d{8,11}\b",            # Telefones (8 a 11 dígitos)
        r"(whatsapp|zap|wpp|telegram|instagram|facebook|insta|fb|celular|telefone)", # Plataformas
        r"(pix|transferência|depósito|conta bancária|banco)", # Pagamentos
    ]

    async def execute(self, sender_id: UUID, dto: SendMessageDTO) -> MessageResponseDTO:
        """
        Executa o envio da mensagem.

        Args:
            sender_id: ID do usuário que envia.
            dto: Dados da mensagem.

        Returns:
            MessageResponseDTO: Mensagem enviada.
        """
        # 1. Validar usuários
        receiver = await self.user_repository.get_by_id(dto.receiver_id)
        if not receiver:
            raise UserNotFoundException(str(dto.receiver_id))

        # 2. Validar agendamento ativo
        has_active = await self._check_active_scheduling(sender_id, dto.receiver_id)
        if not has_active:
            raise ActiveSchedulingRequiredException()

        # 3. Filtrar conteúdo
        self._filter_content(dto.content)

        # 4. Criar e salvar mensagem
        message = Message(
            sender_id=sender_id,
            receiver_id=dto.receiver_id,
            content=dto.content.strip()
        )

        saved_message = await self.message_repository.create(message)

        return MessageResponseDTO(
            id=saved_message.id,
            sender_id=saved_message.sender_id,
            receiver_id=saved_message.receiver_id,
            content=saved_message.content,
            timestamp=saved_message.timestamp,
            is_read=saved_message.is_read
        )

    async def _check_active_scheduling(self, user_a: UUID, user_b: UUID) -> bool:
        """Verifica se existe pelo menos um agendamento ativo entre os usuários."""
        active_statuses = [
            SchedulingStatus.PENDING,
            SchedulingStatus.CONFIRMED,
            SchedulingStatus.RESCHEDULE_REQUESTED,
        ]
        
        # Como o list_by_student/instructor do repositório pode ser limitado,
        # o ideal seria um método específico no repositório, mas podemos usar o que temos
        # ou buscar por ambos os lados.
        
        # Vamos tentar buscar agendamentos onde user_a é aluno e user_b é instrutor
        scheds_as_student = await self.scheduling_repository.list_by_student(
            student_id=user_a,
            status=active_statuses
        )
        for s in scheds_as_student:
            if s.instructor_id == user_b:
                return True

        # Ou onde user_a é instrutor e user_b é aluno
        scheds_as_instructor = await self.scheduling_repository.list_by_instructor(
            instructor_id=user_a,
            status=None # O repositório atual só aceita um status por vez na interface?
        )
        # Ah, o repositório list_by_instructor só aceita um SchedulingStatus ou None.
        # Mas o list_by_student aceita Sequence[SchedulingStatus].
        
        # Vamos verificar se o instrutor tem agendamentos ativos com este aluno.
        # Na verdade, se user_a é instrutor, user_b deve ser aluno.
        # Podemos listar agendamentos do aluno user_b e ver se o instrutor é user_a.
        scheds_b_as_student = await self.scheduling_repository.list_by_student(
            student_id=user_b,
            status=active_statuses
        )
        for s in scheds_b_as_student:
            if s.instructor_id == user_a:
                return True

        return False

    def _filter_content(self, content: str) -> None:
        """Valida se o conteúdo contém padrões proibidos."""
        lowered_content = content.lower()
        
        for pattern in self.PROHIBITED_PATTERNS:
            if re.search(pattern, lowered_content):
                raise ForbiddenContentException()
