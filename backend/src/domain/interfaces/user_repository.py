"""
User Repository Interface

Define o contrato para operações de persistência de usuários.
"""

from typing import Protocol
from uuid import UUID

from src.domain.entities.user import User


class IUserRepository(Protocol):
    """
    Interface para repositório de usuários.

    Implementações concretas devem fornecer persistência (SQLAlchemy, etc).
    """

    async def create(self, user: User) -> User:
        """
        Cria um novo usuário.

        Args:
            user: Entidade de usuário a ser criada.

        Returns:
            User: Usuário criado com ID populado.

        Raises:
            UserAlreadyExistsException: Se email já existir.
        """
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Busca usuário por ID.

        Args:
            user_id: UUID do usuário.

        Returns:
            User | None: Usuário encontrado ou None.
        """
        ...

    async def get_essential_by_id(self, user_id: UUID) -> User | None:
        """
        Busca apenas campos essenciais do usuário por ID (sem senha).

        Args:
            user_id: UUID do usuário.

        Returns:
            User | None: Usuário encontrado ou None.
        """
        ...

    async def get_by_email(self, email: str) -> User | None:
        """
        Busca usuário por email.

        Args:
            email: Email do usuário.

        Returns:
            User | None: Usuário encontrado ou None.
        """
        ...

    async def update(self, user: User) -> User:
        """
        Atualiza um usuário existente.

        Args:
            user: Entidade de usuário com dados atualizados.

        Returns:
            User: Usuário atualizado.
        """
        ...

    async def delete(self, user_id: UUID) -> bool:
        """
        Remove um usuário.

        Args:
            user_id: UUID do usuário a remover.

        Returns:
            bool: True se removido, False se não encontrado.
        """
        ...
