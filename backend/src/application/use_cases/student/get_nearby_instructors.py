"""
Get Nearby Instructors Use Case

Caso de uso otimizado para busca de instrutores próximos com cache.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
import json

from src.application.dtos.profile_dtos import (
    InstructorProfileResponseDTO,
    InstructorSearchDTO,
    InstructorSearchResultDTO,
    LocationResponseDTO,
)
from src.domain.entities.location import Location
from src.domain.exceptions import InvalidLocationException
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.infrastructure.services.pricing_service import PricingService


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
        # Validar coordenadas
        try:
            center = Location(latitude=dto.latitude, longitude=dto.longitude)
        except ValueError as e:
            raise InvalidLocationException(str(e)) from e

        # Tentar buscar do cache
        if self.cache_service:
            cache_key = (
                f"nearby:{dto.latitude}:{dto.longitude}:{dto.radius_km}:"
                f"{dto.biological_sex}:{dto.license_category}:{dto.search_query}"
            )
            cached = await self.cache_service.get(cache_key)

            if cached:
                data = json.loads(cached)
                return InstructorSearchResultDTO(
                    instructors=[
                        InstructorProfileResponseDTO(
                        **{k: v for k, v in inst.items() if k not in ["hourly_rate", "price_cat_a_instructor_vehicle", "price_cat_a_student_vehicle", "price_cat_b_instructor_vehicle", "price_cat_b_student_vehicle"]},
                            hourly_rate=Decimal(inst["hourly_rate"]),
                            price_cat_a_instructor_vehicle=Decimal(inst["price_cat_a_instructor_vehicle"]) if inst.get("price_cat_a_instructor_vehicle") else None,
                            price_cat_a_student_vehicle=Decimal(inst["price_cat_a_student_vehicle"]) if inst.get("price_cat_a_student_vehicle") else None,
                            price_cat_b_instructor_vehicle=Decimal(inst["price_cat_b_instructor_vehicle"]) if inst.get("price_cat_b_instructor_vehicle") else None,
                            price_cat_b_student_vehicle=Decimal(inst["price_cat_b_student_vehicle"]) if inst.get("price_cat_b_student_vehicle") else None,
                        )
                        for inst in data["instructors"]
                    ],
                    total_count=data["total_count"],
                    radius_km=data["radius_km"],
                    center_latitude=data["center_latitude"],
                    center_longitude=data["center_longitude"],
                )

        # Cache miss - buscar no banco
        profiles = await self.instructor_repository.search_by_location(
            center=center,
            radius_km=dto.radius_km,
            biological_sex=dto.biological_sex,
            license_category=dto.license_category,
            search_query=dto.search_query,
            only_available=dto.only_available,
            limit=dto.limit,
        )

        def format_name(full_name: str | None) -> str:
            if not full_name:
                return "Instrutor"
            parts = full_name.split()
            if len(parts) >= 2:
                return f"{parts[0]} {parts[-1]}"
            return full_name

        # Montar resposta
        instructors = []
        for profile in profiles:
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
                    city=profile.city,
                    vehicle_type=profile.vehicle_type,
                    license_category=profile.license_category,
                    hourly_rate=PricingService.calculate_final_price(profile.hourly_rate),
                    rating=profile.rating,
                    total_reviews=profile.total_reviews,
                    is_available=profile.is_available,
                    full_name=format_name(profile.full_name),
                    location=location_dto,
                    distance_km=round(distance, 2) if distance is not None else None,
                    has_mp_account=profile.has_mp_account,
                    price_cat_a_instructor_vehicle=PricingService.calculate_final_price(profile.price_cat_a_instructor_vehicle) if profile.price_cat_a_instructor_vehicle else None,
                    price_cat_a_student_vehicle=PricingService.calculate_final_price(profile.price_cat_a_student_vehicle) if profile.price_cat_a_student_vehicle else None,
                    price_cat_b_instructor_vehicle=PricingService.calculate_final_price(profile.price_cat_b_instructor_vehicle) if profile.price_cat_b_instructor_vehicle else None,
                    price_cat_b_student_vehicle=PricingService.calculate_final_price(profile.price_cat_b_student_vehicle) if profile.price_cat_b_student_vehicle else None,
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
                        "city": inst.city,
                        "vehicle_type": inst.vehicle_type,
                        "license_category": inst.license_category,
                        "hourly_rate": str(inst.hourly_rate),
                        "rating": inst.rating,
                        "total_reviews": inst.total_reviews,
                        "is_available": inst.is_available,
                        "full_name": inst.full_name,
                        "location": {
                            "latitude": inst.location.latitude,
                            "longitude": inst.location.longitude,
                        } if inst.location else None,
                        "distance_km": inst.distance_km,
                        "has_mp_account": inst.has_mp_account,
                        "price_cat_a_instructor_vehicle": str(inst.price_cat_a_instructor_vehicle) if inst.price_cat_a_instructor_vehicle else None,
                        "price_cat_a_student_vehicle": str(inst.price_cat_a_student_vehicle) if inst.price_cat_a_student_vehicle else None,
                        "price_cat_b_instructor_vehicle": str(inst.price_cat_b_instructor_vehicle) if inst.price_cat_b_instructor_vehicle else None,
                        "price_cat_b_student_vehicle": str(inst.price_cat_b_student_vehicle) if inst.price_cat_b_student_vehicle else None,
                    }
                    for inst in instructors
                ],
                "total_count": result.total_count,
                "radius_km": result.radius_km,
                "center_latitude": result.center_latitude,
                "center_longitude": result.center_longitude,
            }
            cache_key = (
                f"nearby:{dto.latitude}:{dto.longitude}:{dto.radius_km}:"
                f"{dto.biological_sex}:{dto.license_category}:{dto.search_query}"
            )
            await self.cache_service.set(
                cache_key,
                json.dumps(cache_data),
                ttl_seconds=60,
            )

        return result
