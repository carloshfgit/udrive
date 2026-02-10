"""
Update Instructor Profile Use Case

Caso de uso para criar ou atualizar perfil de instrutor.
"""

from datetime import datetime
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

        # Atualizar cidade se fornecida (preenchida manualmente pelo instrutor)
        if dto.city is not None:
            profile.city = dto.city

        # Atualizar disponibilidade se fornecida
        if dto.is_available is not None:
            profile.set_availability(dto.is_available)

        # Atualizar dados do usuário se fornecidos
        user_updated = False
        if dto.full_name is not None:
            user.full_name = dto.full_name
            user_updated = True
        if dto.phone is not None:
            user.phone = dto.phone
            user_updated = True
        if dto.cpf is not None:
            user.cpf = dto.cpf
            user_updated = True
        if dto.birth_date is not None:
            user.birth_date = dto.birth_date
            user_updated = True
        if dto.biological_sex is not None:
            user.biological_sex = dto.biological_sex
            user_updated = True

        if user_updated:
            user.updated_at = datetime.utcnow()
            await self.user_repository.update(user)

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
            city=saved_profile.city,
            vehicle_type=saved_profile.vehicle_type,
            license_category=saved_profile.license_category,
            hourly_rate=saved_profile.hourly_rate,
            rating=saved_profile.rating,
            total_reviews=saved_profile.total_reviews,
            is_available=saved_profile.is_available,
            full_name=user.full_name,
            phone=user.phone,
            cpf=user.cpf,
            birth_date=user.birth_date,
            biological_sex=user.biological_sex,
            location=location_dto,
        )
