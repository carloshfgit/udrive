"""
Availability Repository Implementation

Implementação concreta do repositório de disponibilidade.
"""

from datetime import datetime
from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.availability import Availability
from src.domain.interfaces.availability_repository import IAvailabilityRepository
from src.infrastructure.db.models.availability_model import AvailabilityModel


class AvailabilityRepositoryImpl(IAvailabilityRepository):
    """Implementação do repositório de disponibilidade."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, availability: Availability) -> Availability:
        model = AvailabilityModel.from_entity(availability)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def update(self, availability: Availability) -> Availability:
        stmt = select(AvailabilityModel).where(AvailabilityModel.id == availability.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"Disponibilidade {availability.id} não encontrada")

        model.start_time = availability.start_time
        model.end_time = availability.end_time
        model.is_active = availability.is_active
        model.updated_at = availability.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, availability_id: UUID) -> bool:
        stmt = select(AvailabilityModel).where(AvailabilityModel.id == availability_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def get_by_id(self, availability_id: UUID) -> Availability | None:
        stmt = select(AvailabilityModel).where(AvailabilityModel.id == availability_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def list_by_instructor(
        self, instructor_id: UUID, only_active: bool = True
    ) -> Sequence[Availability]:
        stmt = (
            select(AvailabilityModel)
            .where(AvailabilityModel.instructor_id == instructor_id)
            .order_by(AvailabilityModel.day_of_week, AvailabilityModel.start_time)
        )

        if only_active:
            stmt = stmt.where(AvailabilityModel.is_active.is_(True))

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.scalars().all()]

    async def get_by_instructor_and_day(
        self,
        instructor_id: UUID,
        day_of_week: int,
        only_active: bool = True,
    ) -> Sequence[Availability]:
        """Lista slots de um instrutor para um dia específico da semana."""
        stmt = (
            select(AvailabilityModel)
            .where(
                AvailabilityModel.instructor_id == instructor_id,
                AvailabilityModel.day_of_week == day_of_week,
            )
            .order_by(AvailabilityModel.start_time)
        )

        if only_active:
            stmt = stmt.where(AvailabilityModel.is_active.is_(True))

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.scalars().all()]

    async def check_overlap(
        self,
        instructor_id: UUID,
        day_of_week: int,
        start_time: "datetime.time",
        end_time: "datetime.time",
        exclude_id: UUID | None = None,
    ) -> bool:
        """
        Verifica se há sobreposição de horário no mesmo dia para o mesmo instrutor.
        Overlap logic: (StartA < EndB) and (EndA > StartB)
        """
        stmt = select(AvailabilityModel).where(
            AvailabilityModel.instructor_id == instructor_id,
            AvailabilityModel.day_of_week == day_of_week,
            AvailabilityModel.start_time < end_time,
            AvailabilityModel.end_time > start_time,
        )

        if exclude_id:
            stmt = stmt.where(AvailabilityModel.id != exclude_id)

        result = await self._session.execute(stmt)
        return result.first() is not None

    async def is_time_available(
        self,
        instructor_id: UUID,
        target_datetime: "datetime.datetime",
        duration_minutes: int,
    ) -> bool:
        """
        Verifica se o horário específico está coberto por algum slot de disponibilidade ativo.
        """
        from datetime import timedelta

        day = target_datetime.weekday()
        start = target_datetime.time()
        end_dt = target_datetime + timedelta(minutes=duration_minutes)
        end = end_dt.time()

        # Se a aula cruza a meia-noite, a lógica complica.
        # Simplificação: Não permitimos aulas cruzando meia-noite por enquanto com esta estrutura simples.
        # Ou melhor, se cruzar meia-noite, end < start, então devemos tratar.
        # Assumindo que slots não cruzam dias na modelagem atual (start < end constraint).

        if end_dt.date() != target_datetime.date():
             # Se cruza o dia, precisamos verificar se existe slot cobrindo até 23:59 E slot no dia seguinte iniciando 00:00
             # Por simplificação, vamos retornar False para aulas trans-dia por enquanto, exceto se implementarmos lógica complexa.
             return False
        
        stmt = select(AvailabilityModel).where(
            AvailabilityModel.instructor_id == instructor_id,
            AvailabilityModel.day_of_week == day,
            AvailabilityModel.is_active.is_(True),
            AvailabilityModel.start_time <= start,
            AvailabilityModel.end_time >= end,
        )

        result = await self._session.execute(stmt)
        return result.first() is not None
