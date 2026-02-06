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
from src.core.helpers.timezone_utils import DEFAULT_TIMEZONE


class SchedulingRepositoryImpl(ISchedulingRepository):
    """Implementação do repositório de agendamentos usando SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, scheduling: Scheduling) -> Scheduling:
        model = SchedulingModel.from_entity(scheduling)
        self._session.add(model)
        await self._session.flush()
        
        # Reload with relationships to avoid MissingGreenlet error
        # during to_entity() conversion (which accesses .student/.instructor)
        created = await self.get_by_id(model.id)
        if not created:
            # Should not happen after commit
            return model.to_entity()
        return created

    async def get_by_id(self, scheduling_id: UUID) -> Scheduling | None:
        stmt = (
            select(SchedulingModel)
            .where(SchedulingModel.id == scheduling_id)
            .options(
                joinedload(SchedulingModel.student),
                joinedload(SchedulingModel.instructor),
                joinedload(SchedulingModel.review)
            )
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        return model.to_entity() if model else None

    async def update(self, scheduling: Scheduling) -> Scheduling:
        # Busca o modelo existente para garantir que estamos anexados à sessão
        # e para atualizar apenas os campos que mudaram
        stmt = (
            select(SchedulingModel)
            .where(SchedulingModel.id == scheduling.id)
            .options(
                joinedload(SchedulingModel.student),
                joinedload(SchedulingModel.instructor),
                joinedload(SchedulingModel.review)
            )
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()

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
        model.started_at = scheduling.started_at
        model.updated_at = scheduling.updated_at

        # Commit da transação
        await self._session.flush()
        
        # Recarregar o modelo com os relacionamentos necessários para to_entity()
        # Não usamos refresh() simples pois precisamos dos relacionamentos
        # O padrão é buscar novamente com as options
        return (await self.get_by_id(scheduling.id)) or model.to_entity()

    async def delete(self, scheduling_id: UUID) -> bool:
        """Remove um agendamento."""
        stmt = select(SchedulingModel).where(SchedulingModel.id == scheduling_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def list_by_student(
        self,
        student_id: UUID,
        status: SchedulingStatus | Sequence[SchedulingStatus] | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Sequence[Scheduling]:
        stmt = (
            select(SchedulingModel)
            .where(SchedulingModel.student_id == student_id)
            .order_by(SchedulingModel.scheduled_datetime.desc())
            .limit(limit)
            .offset(offset)
            .options(
                joinedload(SchedulingModel.student),
                joinedload(SchedulingModel.instructor),
                joinedload(SchedulingModel.review)
            )
        )

        if status:
            if isinstance(status, (list, tuple, Sequence)):
                stmt = stmt.where(SchedulingModel.status.in_(status))
            else:
                stmt = stmt.where(SchedulingModel.status == status)

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.unique().scalars().all()]

    async def count_by_student(
        self,
        student_id: UUID,
        status: SchedulingStatus | Sequence[SchedulingStatus] | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(SchedulingModel).where(SchedulingModel.student_id == student_id)

        if status:
            if isinstance(status, (list, tuple, Sequence)):
                stmt = stmt.where(SchedulingModel.status.in_(status))
            else:
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
            .options(
                joinedload(SchedulingModel.student),
                joinedload(SchedulingModel.instructor),
                joinedload(SchedulingModel.review)
            )
        )

        if status:
            stmt = stmt.where(SchedulingModel.status == status)

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.unique().scalars().all()]

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
        from datetime import datetime, timezone

        # Criar datetime aware no timezone padrão (Brasília)
        # 00:00:00 do dia alvo em SP
        start_of_day_local = datetime.combine(target_date, datetime.min.time(), tzinfo=DEFAULT_TIMEZONE)
        # 23:59:59.999999 do dia alvo em SP
        end_of_day_local = datetime.combine(target_date, datetime.max.time(), tzinfo=DEFAULT_TIMEZONE)

        # Converter para UTC para consulta no banco
        start_of_day_utc = start_of_day_local.astimezone(timezone.utc)
        end_of_day_utc = end_of_day_local.astimezone(timezone.utc)

        stmt = (
            select(SchedulingModel)
            .where(
                SchedulingModel.instructor_id == instructor_id,
                SchedulingModel.scheduled_datetime >= start_of_day_utc,
                SchedulingModel.scheduled_datetime <= end_of_day_utc,
            )
            .order_by(SchedulingModel.scheduled_datetime.asc())
            .options(
                joinedload(SchedulingModel.student),
                joinedload(SchedulingModel.instructor),
                joinedload(SchedulingModel.review)
            )
        )

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.unique().scalars().all()]

    async def get_scheduling_dates_for_month(
        self,
        instructor_id: UUID,
        year: int,
        month: int,
    ) -> Sequence["date"]:
        """Retorna lista de datas únicas com agendamentos no mês."""
        from calendar import monthrange
        from datetime import datetime, timezone

        # Definir limites do mês no timezone local (Brasília)
        # Dia 1 00:00:00 BRT
        first_day_local = datetime(year, month, 1, 0, 0, 0, tzinfo=DEFAULT_TIMEZONE)
        
        last_day_num = monthrange(year, month)[1]
        # Último dia 23:59:59 BRT
        last_day_local = datetime(year, month, last_day_num, 23, 59, 59, tzinfo=DEFAULT_TIMEZONE)

        # Converter limites para UTC para o filtro WHERE (performance)
        first_day_utc = first_day_local.astimezone(timezone.utc)
        last_day_utc = last_day_local.astimezone(timezone.utc)

        # Para extrair a data correta, precisamos converter o timestamp do banco (UTC)
        # para o timezone local (BRT) ANTES de extrair a data.
        # Postgres: timezone('America/Sao_Paulo', scheduled_datetime)
        
        # O campo é timestamptz. timezone('Zone', timestamptz) retorna timestamp (naive) naquele timezone.
        local_ts = func.timezone(DEFAULT_TIMEZONE.key, SchedulingModel.scheduled_datetime)
        
        stmt = (
            select(func.date(local_ts).label("date"))
            .where(
                SchedulingModel.instructor_id == instructor_id,
                SchedulingModel.scheduled_datetime >= first_day_utc,
                SchedulingModel.scheduled_datetime <= last_day_utc,
                SchedulingModel.status != SchedulingStatus.CANCELLED,
            )
            .distinct()
            .order_by(func.date(local_ts))
        )

        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

