"""
Update Instructor Profile Use Case

Caso de uso para criar ou atualizar perfil de instrutor.
"""

from dataclasses import dataclass

from src.application.dtos.profile_dtos import (
    InstructorProfileResponseDTO,
    LocationResponseDTO,
    UpdateInstructorProfileDTO,
)
from src.domain.entities.instructor_profile import InstructorProfile
from src.domain.entities.location import Location
from src.domain.entities.user_type import UserType
from src.domain.exceptions import InstructorNotFoundException, UserNotFoundException
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class UpdateInstructorProfileUseCase:
    """
    Caso de uso para criar ou atualizar perfil de instrutor.

    Fluxo:
        1. Verificar se usuário existe e é instrutor
        2. Buscar perfil existente ou criar novo
        3. Atualizar campos fornecidos
        4. Persistir alterações
        5. Retornar perfil atualizado
    """

    user_repository: IUserRepository
    instructor_repository: IInstructorRepository

    async def execute(self, dto: UpdateInstructorProfileDTO) -> InstructorProfileResponseDTO:
        """
        Executa a criação ou atualização do perfil.

        Args:
            dto: Dados do perfil a atualizar.

        Returns:
            InstructorProfileResponseDTO: Perfil atualizado.

        Raises:
            UserNotFoundException: Se usuário não existir.
            InstructorNotFoundException: Se usuário não for instrutor.
        """
        # Verificar se usuário existe
        user = await self.user_repository.get_by_id(dto.user_id)
        if user is None:
            raise UserNotFoundException(str(dto.user_id))

        # Verificar se é instrutor
        if user.user_type != UserType.INSTRUCTOR:
            raise InstructorNotFoundException(
                f"Usuário {dto.user_id} não é um instrutor"
            )

        # Buscar perfil existente ou criar novo
        profile = await self.instructor_repository.get_by_user_id(dto.user_id)

        if profile is None:
            # Criar novo perfil
            profile = InstructorProfile(user_id=dto.user_id)

        # Atualizar campos fornecidos
        if dto.bio is not None or dto.vehicle_type is not None or \
           dto.license_category is not None or dto.hourly_rate is not None:
            profile.update_profile(
                bio=dto.bio,
                vehicle_type=dto.vehicle_type,
                license_category=dto.license_category,
                hourly_rate=dto.hourly_rate,
            )

        # Atualizar localização se fornecida
        if dto.latitude is not None and dto.longitude is not None:
            location = Location(latitude=dto.latitude, longitude=dto.longitude)
            profile.update_location(location)

        # Atualizar disponibilidade se fornecida
        if dto.is_available is not None:
            profile.set_availability(dto.is_available)

        # Persistir (criar ou atualizar)
        if await self.instructor_repository.get_by_user_id(dto.user_id) is None:
            saved_profile = await self.instructor_repository.create(profile)
        else:
            saved_profile = await self.instructor_repository.update(profile)

        # Montar resposta
        location_dto = None
        if saved_profile.location:
            location_dto = LocationResponseDTO(
                latitude=saved_profile.location.latitude,
                longitude=saved_profile.location.longitude,
            )

        return InstructorProfileResponseDTO(
            id=saved_profile.id,
            user_id=saved_profile.user_id,
            bio=saved_profile.bio,
            vehicle_type=saved_profile.vehicle_type,
            license_category=saved_profile.license_category,
            hourly_rate=saved_profile.hourly_rate,
            rating=saved_profile.rating,
            total_reviews=saved_profile.total_reviews,
            is_available=saved_profile.is_available,
            location=location_dto,
        )
