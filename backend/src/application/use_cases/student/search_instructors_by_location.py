"""
Search Instructors By Location Use Case

Caso de uso para buscar instrutores por proximidade geográfica.
"""

from dataclasses import dataclass

from src.application.dtos.profile_dtos import (
    InstructorProfileResponseDTO,
    InstructorSearchDTO,
    InstructorSearchResultDTO,
    LocationResponseDTO,
)
from src.domain.entities.location import Location
from src.domain.exceptions import InvalidLocationException
from src.domain.interfaces.instructor_repository import IInstructorRepository


@dataclass
class SearchInstructorsByLocationUseCase:
    """
    Caso de uso para buscar instrutores por proximidade.

    Utiliza queries espaciais do PostGIS para encontrar
    instrutores dentro de um raio configurável.

    Fluxo:
        1. Validar coordenadas de busca
        2. Executar busca espacial via repositório
        3. Calcular distância de cada instrutor
        4. Retornar resultados ordenados por distância
    """

    instructor_repository: IInstructorRepository

    async def execute(self, dto: InstructorSearchDTO) -> InstructorSearchResultDTO:
        """
        Executa a busca de instrutores por localização.

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

        # Validar raio
        if dto.radius_km <= 0:
            raise InvalidLocationException("Raio deve ser maior que zero")

        # Executar busca espacial
        profiles = await self.instructor_repository.search_by_location(
            center=center,
            radius_km=dto.radius_km,
            biological_sex=dto.biological_sex,
            only_available=dto.only_available,
            limit=dto.limit,
        )

        # Montar resposta com distâncias
        instructors = []
        for profile in profiles:
            location_dto = None
            distance = None

            if profile.location:
                location_dto = LocationResponseDTO(
                    latitude=profile.location.latitude,
                    longitude=profile.location.longitude,
                )
                # Calcular distância aproximada
                distance = center.distance_to(profile.location)

            instructors.append(
                InstructorProfileResponseDTO(
                    id=profile.id,
                    user_id=profile.user_id,
                    bio=profile.bio,
                    city=profile.city,
                    vehicle_type=profile.vehicle_type,
                    license_category=profile.license_category,
                    hourly_rate=profile.hourly_rate,
                    rating=profile.rating,
                    total_reviews=profile.total_reviews,
                    is_available=profile.is_available,
                    location=location_dto,
                    distance_km=round(distance, 2) if distance is not None else None,
                    has_mp_account=profile.has_mp_account,
                )
            )

        return InstructorSearchResultDTO(
            instructors=instructors,
            total_count=len(instructors),
            radius_km=dto.radius_km,
            center_latitude=dto.latitude,
            center_longitude=dto.longitude,
        )
