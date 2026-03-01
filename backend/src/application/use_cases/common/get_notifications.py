"""
Get Notifications Use Case

Caso de uso para listar notificações paginadas de um usuário.
"""

from dataclasses import dataclass

from src.application.dtos.notification_dtos import (
    ListNotificationsInput,
    NotificationListResponseDTO,
    NotificationResponseDTO,
)
from src.domain.interfaces.notification_repository import INotificationRepository


@dataclass
class GetNotificationsUseCase:
    """
    Retorna a lista paginada de notificações do usuário com contagem de não-lidas.

    Fluxo:
        1. Buscar notificações paginadas do repositório.
        2. Contar notificações não lidas.
        3. Mapear para DTOs de resposta.
    """

    notification_repository: INotificationRepository

    async def execute(self, dto: ListNotificationsInput) -> NotificationListResponseDTO:
        """
        Executa a listagem de notificações.

        Args:
            dto: Parâmetros de listagem (user_id, limit, offset).

        Returns:
            Lista paginada de notificações com contagem de não-lidas.
        """
        notifications = await self.notification_repository.get_by_user(
            user_id=dto.user_id,
            limit=dto.limit,
            offset=dto.offset,
        )
        unread_count = await self.notification_repository.count_unread(dto.user_id)

        response_items = [
            NotificationResponseDTO(
                id=n.id,
                type=n.type.value,
                title=n.title,
                body=n.body,
                action_type=n.action_type.value if n.action_type else None,
                action_id=n.action_id,
                is_read=n.is_read,
                created_at=n.created_at,
                read_at=n.read_at,
            )
            for n in notifications
        ]

        return NotificationListResponseDTO(
            notifications=response_items,
            unread_count=unread_count,
            total=len(response_items),
            limit=dto.limit,
            offset=dto.offset,
            has_more=len(response_items) == dto.limit,
        )
