"""
ILocationService Interface

Interface para serviço de geolocalização.
"""

from abc import ABC, abstractmethod

from src.domain.entities.instructor_profile import InstructorProfile
from src.domain.entities.location import Location


class ILocationService(ABC):
    """
    Interface abstrata para serviço de geolocalização.

    Define operações de cálculo de distância e busca espacial.
    """

    @abstractmethod
    def calculate_distance(self, point_a: Location, point_b: Location) -> float:
        """
        Calcula distância entre dois pontos em quilômetros.

        Args:
            point_a: Primeira localização.
            point_b: Segunda localização.

        Returns:
            Distância em quilômetros.
        """
        ...

    @abstractmethod
    async def get_instructors_in_radius(
        self,
        center: Location,
        radius_km: float,
        only_available: bool = True,
    ) -> list[InstructorProfile]:
        """
        Busca instrutores dentro de um raio.

        Args:
            center: Centro da busca.
            radius_km: Raio em quilômetros.
            only_available: Se True, filtra apenas disponíveis.

        Returns:
            Lista de instrutores dentro do raio, ordenados por distância.
        """
        ...

    @abstractmethod
    def is_within_radius(
        self,
        point: Location,
        center: Location,
        radius_km: float,
    ) -> bool:
        """
        Verifica se um ponto está dentro de um raio.

        Args:
            point: Ponto a verificar.
            center: Centro do raio.
            radius_km: Raio em quilômetros.

        Returns:
            True se o ponto está dentro do raio.
        """
        ...
