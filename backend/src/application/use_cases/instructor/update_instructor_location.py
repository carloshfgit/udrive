"""
Update Instructor Location Use Case

Caso de uso otimizado para atualização frequente de localização.
"""

from dataclasses import dataclass

from src.application.dtos.profile_dtos import UpdateLocationDTO
from src.domain.entities.location import Location
from src.domain.exceptions import (
    InstructorNotFoundException,
    InvalidLocationException,
)
from src.domain.interfaces.instructor_repository import IInstructorRepository


@dataclass
class UpdateInstructorLocationUseCase:
    """
    Caso de uso para atualização de localização em tempo real.

    Otimizado para updates frequentes (a cada 5-30s conforme movimento).
    Não carrega o perfil completo, apenas atualiza a coluna de geometria.

    Fluxo:
        1. Validar coordenadas
        2. Atualizar localização diretamente no banco
        3. Invalidar cache se necessário
    """

    instructor_repository: IInstructorRepository

    async def execute(self, dto: UpdateLocationDTO) -> bool:
        """
        Atualiza a localização do instrutor.

        Args:
            dto: Dados da nova localização.

        Returns:
            True se atualizado com sucesso.

        Raises:
            InvalidLocationException: Se coordenadas forem inválidas.
            InstructorNotFoundException: Se perfil não existir.
        """
        # Validar coordenadas
        try:
            location = Location(latitude=dto.latitude, longitude=dto.longitude)
        except ValueError as e:
            raise InvalidLocationException(str(e)) from e

        # Atualizar localização (operação otimizada)
        updated = await self.instructor_repository.update_location(
            user_id=dto.user_id,
            location=location,
        )

        if not updated:
            raise InstructorNotFoundException(str(dto.user_id))

        return True
