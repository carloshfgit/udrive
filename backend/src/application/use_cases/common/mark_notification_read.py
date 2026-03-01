"""
Mark Notification As Read Use Case

Caso de uso para marcar notificação(ões) como lidas.
"""

from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.notification_dtos import MarkAsReadInput, UnreadCountDTO
from src.domain.exceptions import NotificationNotFoundException
from src.domain.interfaces.notification_repository import INotificationRepository


@dataclass
class MarkAsReadUseCase:
    """
    Marca uma ou todas as notificações de um usuário como lidas.

    Garante ownership: o usuário só pode marcar suas próprias notificações.
    """

    notification_repository: INotificationRepository

    async def execute_one(self, dto: MarkAsReadInput) -> UnreadCountDTO:
        """
        Marca uma notificação específica como lida.

        Args:
            dto: ID da notificação e ID do usuário.

        Returns:
            Contagem atualizada de não-lidas.

        Raises:
            NotificationNotFoundException: Se a notificação não for encontrada.
        """
        success = await self.notification_repository.mark_as_read(
            notification_id=dto.notification_id,
            user_id=dto.user_id,
        )
        if not success:
            raise NotificationNotFoundException(str(dto.notification_id))

        unread = await self.notification_repository.count_unread(dto.user_id)
        return UnreadCountDTO(count=unread)

    async def execute_all(self, user_id: UUID) -> UnreadCountDTO:
        """
        Marca todas as notificações do usuário como lidas.

        Args:
            user_id: ID do usuário.

        Returns:
            Contagem de não-lidas (deve ser 0).
        """
        await self.notification_repository.mark_all_as_read(user_id)
        return UnreadCountDTO(count=0)
