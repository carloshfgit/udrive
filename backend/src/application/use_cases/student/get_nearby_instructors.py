"""
Get Nearby Instructors Use Case

Caso de uso otimizado para busca de instrutores próximos com cache.
"""

from dataclasses import dataclass
from typing import Protocol

from src.application.dtos.profile_dtos import (
    InstructorProfileResponseDTO,
    InstructorSearchDTO,
    InstructorSearchResultDTO,
    LocationResponseDTO,
)
from src.domain.entities.location import Location
from src.domain.exceptions import InvalidLocationException
from src.domain.interfaces.instructor_repository import IInstructorRepository


class ICacheService(Protocol):
    """Interface para serviço de cache."""

    async def get(self, key: str) -> str | None:
        """Obtém valor do cache."""
        ...

    async def set(self, key: str, value: str, ttl_seconds: int = 60) -> None:
        """Define valor no cache."""
        ...

    async def delete(self, key: str) -> None:
        """Remove valor do cache."""
        ...


@dataclass
class GetNearbyInstructorsUseCase:
    """
    Caso de uso para busca otimizada de instrutores próximos.

    Utiliza cache Redis para melhorar performance em buscas frequentes.
    O cache é baseado em grid (arredondamento de coordenadas).

    Fluxo:
        1. Verificar cache para a região
        2. Se cache miss, executar busca no banco
        3. Armazenar resultado em cache (TTL 60s)
        4. Retornar resultados
    """

    instructor_repository: IInstructorRepository
    cache_service: ICacheService | None = None

    def _get_cache_key(self, lat: float, lon: float, radius: float) -> str:
        """
        Gera chave de cache baseada em grid.

        Arredonda coordenadas para precisão de ~1km para agrupar buscas.
        """
        # Arredonda para 2 casas decimais (~1km de precisão)
        grid_lat = round(lat, 2)
        grid_lon = round(lon, 2)
        return f"instructors:nearby:{grid_lat}:{grid_lon}:{radius}"

    async def execute(self, dto: InstructorSearchDTO) -> InstructorSearchResultDTO:
        """
        Busca instrutores próximos com cache.

        Args:
            dto: Parâmetros da busca.

        Returns:
            InstructorSearchResultDTO: Resultados da busca.

        Raises:
            InvalidLocationException: Se coordenadas forem inválidas.
        """
        import json

        # Validar coordenadas
        try:
            center = Location(latitude=dto.latitude, longitude=dto.longitude)
        except ValueError as e:
            raise InvalidLocationException(str(e)) from e

        # Tentar obter do cache
        if self.cache_service:
            cache_key = self._get_cache_key(dto.latitude, dto.longitude, dto.radius_km)
            cached = await self.cache_service.get(cache_key)

            if cached:
                data = json.loads(cached)
                return InstructorSearchResultDTO(
                    instructors=[
                        InstructorProfileResponseDTO(**inst)
                        for inst in data["instructors"]
                    ],
                    total_count=data["total_count"],
                    radius_km=data["radius_km"],
                    center_latitude=data["center_latitude"],
                    center_longitude=data["center_longitude"],
                )

        # Cache miss - buscar no banco
        # 1. Buscar instrutores COM localização (ordenados por distância)
        profiles_with_location = await self.instructor_repository.search_by_location(
            center=center,
            radius_km=dto.radius_km,
            only_available=dto.only_available,
            limit=dto.limit,
        )

        # 2. Buscar TODOS os instrutores disponíveis (inclui os sem localização)
        all_available = await self.instructor_repository.get_available_instructors(
            limit=dto.limit,
        )

        # 3. Identificar instrutores sem localização (não incluídos na busca espacial)
        ids_with_location = {p.id for p in profiles_with_location}
        profiles_without_location = [
            p for p in all_available
            if p.id not in ids_with_location and p.location is None
        ]

        # Montar resposta - instrutores com localização primeiro
        instructors = []
        for profile in profiles_with_location:
            location_dto = None
            distance = None

            if profile.location:
                location_dto = LocationResponseDTO(
                    latitude=profile.location.latitude,
                    longitude=profile.location.longitude,
                )
                distance = center.distance_to(profile.location)

            instructors.append(
                InstructorProfileResponseDTO(
                    id=profile.id,
                    user_id=profile.user_id,
                    bio=profile.bio,
                    vehicle_type=profile.vehicle_type,
                    license_category=profile.license_category,
                    hourly_rate=profile.hourly_rate,
                    rating=profile.rating,
                    total_reviews=profile.total_reviews,
                    is_available=profile.is_available,
                    location=location_dto,
                    distance_km=round(distance, 2) if distance is not None else None,
                )
            )

        # Adicionar instrutores SEM localização ao final
        for profile in profiles_without_location:
            instructors.append(
                InstructorProfileResponseDTO(
                    id=profile.id,
                    user_id=profile.user_id,
                    bio=profile.bio,
                    vehicle_type=profile.vehicle_type,
                    license_category=profile.license_category,
                    hourly_rate=profile.hourly_rate,
                    rating=profile.rating,
                    total_reviews=profile.total_reviews,
                    is_available=profile.is_available,
                    location=None,  # Sem localização
                    distance_km=None,  # Distância desconhecida
                )
            )

        result = InstructorSearchResultDTO(
            instructors=instructors,
            total_count=len(instructors),
            radius_km=dto.radius_km,
            center_latitude=dto.latitude,
            center_longitude=dto.longitude,
        )

        # Armazenar em cache (TTL 60s)
        if self.cache_service:
            cache_data = {
                "instructors": [
                    {
                        "id": str(inst.id),
                        "user_id": str(inst.user_id),
                        "bio": inst.bio,
                        "vehicle_type": inst.vehicle_type,
                        "license_category": inst.license_category,
                        "hourly_rate": str(inst.hourly_rate),
                        "rating": inst.rating,
                        "total_reviews": inst.total_reviews,
                        "is_available": inst.is_available,
                        "location": {
                            "latitude": inst.location.latitude,
                            "longitude": inst.location.longitude,
                        } if inst.location else None,
                        "distance_km": inst.distance_km,
                    }
                    for inst in instructors
                ],
                "total_count": result.total_count,
                "radius_km": result.radius_km,
                "center_latitude": result.center_latitude,
                "center_longitude": result.center_longitude,
            }
            await self.cache_service.set(
                cache_key,
                json.dumps(cache_data),
                ttl_seconds=60,
            )

        return result
