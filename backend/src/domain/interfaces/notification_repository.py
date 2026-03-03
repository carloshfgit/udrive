"""
INotificationRepository Interface

Interface abstrata para repositório de notificações.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.notification import Notification


class INotificationRepository(ABC):
    """
    Interface abstrata para repositório de notificações.

    Define as operações de persistência e consulta de notificações de usuários.
    """

    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        """
        Persiste uma nova notificação.

        Args:
            notification: Entidade de notificação a ser criada.

        Returns:
            Notificação criada com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """
        Retorna notificações do usuário ordenadas da mais recente para a mais antiga.

        Args:
            user_id: ID do usuário.
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de notificações do usuário.
        """
        ...

    @abstractmethod
    async def count_unread(self, user_id: UUID) -> int:
        """
        Conta notificações não lidas do usuário.

        Args:
            user_id: ID do usuário.

        Returns:
            Número de notificações não lidas.
        """
        ...

    @abstractmethod
    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """
        Marca uma notificação específica como lida.

        Args:
            notification_id: ID da notificação.
            user_id: ID do usuário dono da notificação (validação de ownership).

        Returns:
            True se marcada com sucesso, False se não encontrada.
        """
        ...

    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> int:
        """
        Marca todas as notificações não lidas do usuário como lidas.

        Args:
            user_id: ID do usuário.

        Returns:
            Quantidade de notificações atualizadas.
        """
        ...

    @abstractmethod
    async def delete_read_notifications(self, user_id: UUID) -> int:
        """
        Exclui todas as notificações já lidas do usuário.

        Args:
            user_id: ID do usuário.

        Returns:
            Quantidade de notificações excluídas.
        """
        ...
