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

    async def get_city_name(self, location: Location) -> str | None:
        """
        Obtém o nome da cidade a partir de coordenadas (Nominatim OSM).
        
        Nota: Nominatim requer um User-Agent descritivo e tem limites de uso.
        Para produção, considere Google Maps ou Mapbox.
        """
        import httpx
        import structlog

        logger = structlog.get_logger()
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": location.latitude,
            "lon": location.longitude,
            "format": "json",
            "addressdetails": 1,
        }
        headers = {
            "User-Agent": "GoDrive-App/1.0 (contact@godrive.com)"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                address = data.get("address", {})
                # Tenta obter cidade, município ou vila
                city = (
                    address.get("city") or 
                    address.get("town") or 
                    address.get("village") or 
                    address.get("municipality")
                )
                return city
        except Exception as e:
            logger.error("geocoding_error", error=str(e), lat=location.latitude, lon=location.longitude)
            return None
