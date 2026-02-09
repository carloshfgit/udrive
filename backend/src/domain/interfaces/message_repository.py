"""
IMessageRepository Interface

Interface para repositório de mensagens de chat.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.message import Message


class IMessageRepository(ABC):
    """
    Interface abstrata para repositório de mensagens.
    """

    @abstractmethod
    async def create(self, message: Message) -> Message:
        """
        Salva uma nova mensagem.

        Args:
            message: Mensagem a ser criada.

        Returns:
            Mensagem criada com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Message | None:
        """
        Busca mensagem por ID.

        Args:
            message_id: ID da mensagem.

        Returns:
            Mensagem encontrada ou None.
        """
        ...

    @abstractmethod
    async def list_by_conversation(
        self,
        user_a: UUID,
        user_b: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        """
        Lista mensagens entre dois usuários.

        Args:
            user_a: ID do primeiro usuário.
            user_b: ID do segundo usuário.
            limit: Número máximo de resultados.
            offset: Deslocamento para paginação.

        Returns:
            Lista de mensagens ordenadas por timestamp (mais recentes primeiro ou conforme UI).
        """
        ...

    @abstractmethod
    async def mark_as_read(self, message_ids: list[UUID]) -> None:
        """
        Marca um conjunto de mensagens como lidas.

        Args:
            message_ids: Lista de IDs das mensagens.
        """
        ...

    @abstractmethod
    async def get_last_message_between(self, user_a: UUID, user_b: UUID) -> Message | None:
        """
        Busca a última mensagem trocada entre dois usuários.

        Args:
            user_a: ID do primeiro usuário.
            user_b: ID do segundo usuário.

        Returns:
            A última mensagem ou None.
        """
        ...
