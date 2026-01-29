"""
LocationService Implementation

Implementação concreta do serviço de geolocalização.
"""

from src.domain.entities.instructor_profile import InstructorProfile
from src.domain.entities.location import Location
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.location_service import ILocationService


class LocationServiceImpl(ILocationService):
    """
    Implementação do serviço de geolocalização.

    Utiliza o repositório de instrutores para queries espaciais.
    """

    def __init__(self, instructor_repository: IInstructorRepository) -> None:
        self._instructor_repo = instructor_repository

    def calculate_distance(self, point_a: Location, point_b: Location) -> float:
        """Calcula distância entre dois pontos usando Haversine."""
        return point_a.distance_to(point_b)

    async def get_instructors_in_radius(
        self,
        center: Location,
        radius_km: float,
        only_available: bool = True,
    ) -> list[InstructorProfile]:
        """Busca instrutores dentro de um raio."""
        return await self._instructor_repo.search_by_location(
            center=center,
            radius_km=radius_km,
            only_available=only_available,
        )

    def is_within_radius(
        self,
        point: Location,
        center: Location,
        radius_km: float,
    ) -> bool:
        """Verifica se um ponto está dentro de um raio."""
        distance = self.calculate_distance(point, center)
        return distance <= radius_km
