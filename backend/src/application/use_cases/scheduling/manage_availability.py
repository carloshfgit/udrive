"""
Manage Availability Use Case

Caso de uso para gerenciar slots de disponibilidade do instrutor.
"""

from dataclasses import dataclass

from src.application.dtos.scheduling_dtos import (
    AvailabilityListResponseDTO,
    AvailabilityResponseDTO,
    CreateAvailabilityDTO,
    DeleteAvailabilityDTO,
    UpdateAvailabilityDTO,
)
from src.domain.entities.availability import Availability
from src.domain.entities.user_type import UserType
from src.domain.exceptions import (
    AvailabilityNotFoundException,
    AvailabilityOverlapException,
    InstructorNotFoundException,
    InvalidAvailabilityTimeException,
    UserNotFoundException,
)
from src.domain.interfaces.availability_repository import IAvailabilityRepository
from src.domain.interfaces.user_repository import IUserRepository


@dataclass
class ManageAvailabilityUseCase:
    """
    Caso de uso para gerenciar disponibilidade do instrutor.

    Métodos:
        - create: Criar novo slot
        - update: Atualizar slot existente
        - delete: Remover slot
        - list: Listar todos os slots do instrutor
    """

    availability_repository: IAvailabilityRepository
    user_repository: IUserRepository

    async def create(self, dto: CreateAvailabilityDTO) -> AvailabilityResponseDTO:
        """
        Cria um novo slot de disponibilidade.

        Args:
            dto: Dados do slot a criar.

        Returns:
            AvailabilityResponseDTO: Slot criado.

        Raises:
            InstructorNotFoundException: Se instrutor não existir.
            InvalidAvailabilityTimeException: Se intervalo de tempo inválido.
            AvailabilityOverlapException: Se houver sobreposição.
        """
        # Validar instrutor
        user = await self.user_repository.get_by_id(dto.instructor_id)
        if user is None:
            raise UserNotFoundException(str(dto.instructor_id))
        if user.user_type != UserType.INSTRUCTOR:
            raise InstructorNotFoundException(
                f"Usuário {dto.instructor_id} não é um instrutor"
            )

        # Validar intervalo de tempo
        if dto.start_time >= dto.end_time:
            raise InvalidAvailabilityTimeException(
                "Hora de início deve ser anterior à hora de término"
            )

        # Verificar sobreposição
        has_overlap = await self.availability_repository.check_overlap(
            instructor_id=dto.instructor_id,
            day_of_week=dto.day_of_week,
            start_time=dto.start_time,
            end_time=dto.end_time,
        )
        if has_overlap:
            raise AvailabilityOverlapException()

        # Criar slot
        availability = Availability(
            instructor_id=dto.instructor_id,
            day_of_week=dto.day_of_week,
            start_time=dto.start_time,
            end_time=dto.end_time,
        )

        saved = await self.availability_repository.create(availability)
        return self._to_response_dto(saved)

    async def update(self, dto: UpdateAvailabilityDTO) -> AvailabilityResponseDTO:
        """
        Atualiza um slot de disponibilidade existente.

        Args:
            dto: Dados da atualização.

        Returns:
            AvailabilityResponseDTO: Slot atualizado.

        Raises:
            AvailabilityNotFoundException: Se slot não existir.
            InvalidAvailabilityTimeException: Se intervalo inválido.
            AvailabilityOverlapException: Se houver sobreposição.
        """
        # Buscar slot
        availability = await self.availability_repository.get_by_id(dto.availability_id)
        if availability is None:
            raise AvailabilityNotFoundException(str(dto.availability_id))

        # Verificar permissão
        if availability.instructor_id != dto.instructor_id:
            raise AvailabilityNotFoundException(
                f"Slot {dto.availability_id} não pertence ao instrutor"
            )

        # Calcular novos valores
        new_start = dto.start_time if dto.start_time is not None else availability.start_time
        new_end = dto.end_time if dto.end_time is not None else availability.end_time

        # Validar intervalo
        if new_start >= new_end:
            raise InvalidAvailabilityTimeException(
                "Hora de início deve ser anterior à hora de término"
            )

        # Verificar sobreposição (excluindo o próprio slot)
        if dto.start_time is not None or dto.end_time is not None:
            has_overlap = await self.availability_repository.check_overlap(
                instructor_id=dto.instructor_id,
                day_of_week=availability.day_of_week,
                start_time=new_start,
                end_time=new_end,
                exclude_id=dto.availability_id,
            )
            if has_overlap:
                raise AvailabilityOverlapException()

        # Atualizar
        availability.update(
            start_time=dto.start_time,
            end_time=dto.end_time,
            is_active=dto.is_active,
        )

        saved = await self.availability_repository.update(availability)
        return self._to_response_dto(saved)

    async def delete(self, dto: DeleteAvailabilityDTO) -> bool:
        """
        Remove um slot de disponibilidade.

        Args:
            dto: Dados para remoção.

        Returns:
            True se removido com sucesso.

        Raises:
            AvailabilityNotFoundException: Se slot não existir ou não pertencer ao instrutor.
        """
        # Buscar slot
        availability = await self.availability_repository.get_by_id(dto.availability_id)
        if availability is None:
            raise AvailabilityNotFoundException(str(dto.availability_id))

        # Verificar permissão
        if availability.instructor_id != dto.instructor_id:
            raise AvailabilityNotFoundException(
                f"Slot {dto.availability_id} não pertence ao instrutor"
            )

        return await self.availability_repository.delete(dto.availability_id)

    async def list(self, instructor_id: str) -> AvailabilityListResponseDTO:
        """
        Lista todos os slots de disponibilidade de um instrutor.

        Args:
            instructor_id: ID do instrutor (UUID string).

        Returns:
            AvailabilityListResponseDTO: Lista de slots.

        Raises:
            InstructorNotFoundException: Se instrutor não existir.
        """
        from uuid import UUID

        instructor_uuid = UUID(instructor_id)

        # Validar instrutor
        user = await self.user_repository.get_by_id(instructor_uuid)
        if user is None:
            raise UserNotFoundException(instructor_id)
        if user.user_type != UserType.INSTRUCTOR:
            raise InstructorNotFoundException(
                f"Usuário {instructor_id} não é um instrutor"
            )

        # Listar slots
        availabilities = await self.availability_repository.list_by_instructor(
            instructor_id=instructor_uuid,
            only_active=False,  # Retorna todos para gerenciamento
        )

        # Converter para DTOs
        availability_dtos = [
            self._to_response_dto(a) for a in availabilities
        ]

        return AvailabilityListResponseDTO(
            availabilities=availability_dtos,
            instructor_id=instructor_uuid,
            total_count=len(availability_dtos),
        )

    def _to_response_dto(self, availability: Availability) -> AvailabilityResponseDTO:
        """Converte entidade para DTO de resposta."""
        return AvailabilityResponseDTO(
            id=availability.id,
            instructor_id=availability.instructor_id,
            day_of_week=availability.day_of_week,
            day_name=availability.day_name,
            start_time=availability.start_time.strftime("%H:%M"),
            end_time=availability.end_time.strftime("%H:%M"),
            is_active=availability.is_active,
            duration_minutes=availability.duration_minutes,
        )
