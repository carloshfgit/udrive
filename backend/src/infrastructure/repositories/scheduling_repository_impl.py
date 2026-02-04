"""
Scheduling Repository Implementation

Implementação concreta do repositório de agendamentos.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.infrastructure.db.models.scheduling_model import SchedulingModel


class SchedulingRepositoryImpl(ISchedulingRepository):
    """Implementação do repositório de agendamentos usando SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, scheduling: Scheduling) -> Scheduling:
        model = SchedulingModel.from_entity(scheduling)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model.to_entity()

    async def get_by_id(self, scheduling_id: UUID) -> Scheduling | None:
        stmt = (
            select(SchedulingModel)
            .where(SchedulingModel.id == scheduling_id)
            # Carregar relacionamentos para evitar N+1 queries se necessário depois
            # .options(joinedload(SchedulingModel.student), joinedload(SchedulingModel.instructor))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def update(self, scheduling: Scheduling) -> Scheduling:
        # Busca o modelo existente para garantir que estamos anexados à sessão
        # e para atualizar apenas os campos que mudaram
        stmt = select(SchedulingModel).where(SchedulingModel.id == scheduling.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            # Se não encontrado, poderia lançar erro ou tentar criar
            # O comportamento esperado é atualizar um existente
            raise ValueError(f"Agendamento {scheduling.id} não encontrado para atualização")

        # Atualizar campos
        model.status = scheduling.status
        model.cancellation_reason = scheduling.cancellation_reason
        model.cancelled_by = scheduling.cancelled_by
        model.cancelled_at = scheduling.cancelled_at
        model.completed_at = scheduling.completed_at
        model.updated_at = scheduling.updated_at

        # Commit da transação
        await self._session.commit()
        await self._session.refresh(model)
        return model.to_entity()

    async def delete(self, scheduling_id: UUID) -> bool:
        """Remove um agendamento."""
        stmt = select(SchedulingModel).where(SchedulingModel.id == scheduling_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self._session.delete(model)
        await self._session.commit()
        return True

    async def list_by_student(
        self,
        student_id: UUID,
        status: SchedulingStatus | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[Scheduling]:
        stmt = (
            select(SchedulingModel)
            .where(SchedulingModel.student_id == student_id)
            .order_by(SchedulingModel.scheduled_datetime.desc())
            .limit(limit)
            .offset(offset)
        )

        if status:
            stmt = stmt.where(SchedulingModel.status == status)

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.scalars().all()]

    async def count_by_student(
        self, student_id: UUID, status: SchedulingStatus | None = None
    ) -> int:
        stmt = select(func.count()).select_from(SchedulingModel).where(SchedulingModel.student_id == student_id)

        if status:
            stmt = stmt.where(SchedulingModel.status == status)

        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def list_by_instructor(
        self,
        instructor_id: UUID,
        status: SchedulingStatus | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[Scheduling]:
        stmt = (
            select(SchedulingModel)
            .where(SchedulingModel.instructor_id == instructor_id)
            .order_by(SchedulingModel.scheduled_datetime.desc())
            .limit(limit)
            .offset(offset)
        )

        if status:
            stmt = stmt.where(SchedulingModel.status == status)

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.scalars().all()]

    async def count_by_instructor(
        self, instructor_id: UUID, status: SchedulingStatus | None = None
    ) -> int:
        stmt = select(func.count()).select_from(SchedulingModel).where(SchedulingModel.instructor_id == instructor_id)

        if status:
            stmt = stmt.where(SchedulingModel.status == status)

        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def check_conflict(
        self, instructor_id: UUID, scheduled_datetime: "datetime", duration_minutes: int
    ) -> bool:
        """
        Verifica se existe conflito de horário para o instrutor.
        Conflito ocorre se um agendamento existente se sobrepõe ao novo horário.
        Ignora agendamentos cancelados.
        """
        from datetime import timedelta

        new_start = scheduled_datetime
        new_end = scheduled_datetime + timedelta(minutes=duration_minutes)

        # Lógica de sobreposição:
        # (StartA < EndB) and (EndA > StartB)
        # Onde A é o agendamento existente e B é o novo

        stmt = select(SchedulingModel).where(
            SchedulingModel.instructor_id == instructor_id,
            SchedulingModel.status != SchedulingStatus.CANCELLED,
            SchedulingModel.scheduled_datetime < new_end,
            (SchedulingModel.scheduled_datetime + func.make_interval(0, 0, 0, 0, 0, SchedulingModel.duration_minutes)) > new_start
        )
        
        # Nota: `func.make_interval` é específico do Postgres.
        # Alternativa portátil seria calcular end_time na aplicação ou persistir end_time no banco.
        # Como usamos Postgres + PostGIS, make_interval é aceitável.
        # Mas para garantir robustez, vamos usar datetime puro se possível, mas no 'where' precisamos de expressão SQL.
        # Outra opção: adicionar coluna `end_datetime` no modelo para facilitar queries, mas vamos usar aritmética de data por enquanto.

        result = await self._session.execute(stmt)
        return result.first() is not None

    async def list_by_instructor_and_date(
        self,
        instructor_id: UUID,
        target_date: "date",
    ) -> Sequence[Scheduling]:
        """Lista agendamentos do instrutor para uma data específica."""
        from datetime import datetime, timedelta

        # Início e fim do dia
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        stmt = (
            select(SchedulingModel)
            .where(
                SchedulingModel.instructor_id == instructor_id,
                SchedulingModel.scheduled_datetime >= start_of_day,
                SchedulingModel.scheduled_datetime <= end_of_day,
            )
            .order_by(SchedulingModel.scheduled_datetime.asc())
        )

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.scalars().all()]
