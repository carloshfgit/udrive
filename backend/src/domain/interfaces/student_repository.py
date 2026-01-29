"""
IStudentRepository Interface

Interface para repositório de perfis de alunos.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.student_profile import StudentProfile


class IStudentRepository(ABC):
    """
    Interface abstrata para repositório de alunos.

    Define operações CRUD para perfis de alunos.
    """

    @abstractmethod
    async def create(self, profile: StudentProfile) -> StudentProfile:
        """
        Cria um novo perfil de aluno.

        Args:
            profile: Perfil a ser criado.

        Returns:
            Perfil criado com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, profile_id: UUID) -> StudentProfile | None:
        """
        Busca perfil por ID.

        Args:
            profile_id: ID do perfil.

        Returns:
            Perfil encontrado ou None.
        """
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> StudentProfile | None:
        """
        Busca perfil pelo ID do usuário.

        Args:
            user_id: ID do usuário associado.

        Returns:
            Perfil encontrado ou None.
        """
        ...

    @abstractmethod
    async def update(self, profile: StudentProfile) -> StudentProfile:
        """
        Atualiza um perfil existente.

        Args:
            profile: Perfil com dados atualizados.

        Returns:
            Perfil atualizado.
        """
        ...

    @abstractmethod
    async def delete(self, profile_id: UUID) -> bool:
        """
        Remove um perfil.

        Args:
            profile_id: ID do perfil a remover.

        Returns:
            True se removido, False se não encontrado.
        """
        ...
