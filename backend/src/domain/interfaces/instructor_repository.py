"""
IInstructorRepository Interface

Interface para repositório de perfis de instrutores.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.instructor_profile import InstructorProfile
from src.domain.entities.location import Location


class IInstructorRepository(ABC):
    """
    Interface abstrata para repositório de instrutores.

    Define operações CRUD e busca geolocalizada para perfis de instrutores.
    """

    @abstractmethod
    async def create(self, profile: InstructorProfile) -> InstructorProfile:
        """
        Cria um novo perfil de instrutor.

        Args:
            profile: Perfil a ser criado.

        Returns:
            Perfil criado com ID persistido.
        """
        ...

    @abstractmethod
    async def get_by_id(self, profile_id: UUID) -> InstructorProfile | None:
        """
        Busca perfil por ID.

        Args:
            profile_id: ID do perfil.

        Returns:
            Perfil encontrado ou None.
        """
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> InstructorProfile | None:
        """
        Busca perfil pelo ID do usuário.

        Args:
            user_id: ID do usuário associado.

        Returns:
            Perfil encontrado ou None.
        """
        ...

    @abstractmethod
    async def get_by_mp_user_id(self, mp_user_id: str) -> InstructorProfile | None:
        """
        Busca perfil do instrutor pelo ID de usuário do Mercado Pago.

        Args:
            mp_user_id: O user_id retornado pelo Mercado Pago (OAuth).

        Returns:
            Perfil encontrado ou None.
        """
        ...

    @abstractmethod
    async def get_public_profile_by_user_id(self, user_id: UUID) -> InstructorProfile | None:
        """
        Busca apenas dados públicos do perfil do instrutor.

        Args:
            user_id: ID do usuário associado.

        Returns:
            Perfil encontrado ou None.
        """
        ...

    @abstractmethod
    async def update(self, profile: InstructorProfile) -> InstructorProfile:
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

    @abstractmethod
    async def search_by_location(
        self,
        center: Location,
        radius_km: float = 10.0,
        biological_sex: str | None = None,
        license_category: str | None = None,
        search_query: str | None = None,
        only_available: bool = True,
        limit: int = 50,
    ) -> list[InstructorProfile]:
        """
        Busca instrutores por proximidade geográfica.

        Args:
            center: Localização central da busca.
            radius_km: Raio de busca em quilômetros.
            only_available: Se True, retorna apenas instrutores disponíveis.
            limit: Número máximo de resultados.

        Returns:
            Lista de perfis ordenados por distância.
        """
        ...

    @abstractmethod
    async def update_location(self, user_id: UUID, location: Location, city: str | None = None) -> bool:
        """
        Atualiza apenas a localização (e opcionalmente a cidade) do instrutor.

        Operação otimizada para updates frequentes de posição.

        Args:
            user_id: ID do usuário instrutor.
            location: Nova localização.
            city: Nova cidade (opcional).

        Returns:
            True se atualizado, False se perfil não encontrado.
        """
        ...

    @abstractmethod
    async def get_available_instructors(
        self,
        biological_sex: str | None = None,
        license_category: str | None = None,
        limit: int = 100,
    ) -> list[InstructorProfile]:
        """
        Lista instrutores disponíveis.

        Args:
            limit: Número máximo de resultados.

        Returns:
            Lista de perfis de instrutores disponíveis.
        """
        ...
