"""
Scheduling Repository Implementation

Implementação concreta do repositório de agendamentos.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import contains_eager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from src.domain.entities.scheduling import Scheduling
from src.domain.entities.scheduling_status import SchedulingStatus
from src.domain.interfaces.scheduling_repository import ISchedulingRepository
from src.infrastructure.db.models.scheduling_model import SchedulingModel
from src.infrastructure.db.models.user_model import UserModel
from src.core.helpers.timezone_utils import DEFAULT_TIMEZONE


class SchedulingRepositoryImpl(ISchedulingRepository):
    """Implementação do repositório de agendamentos usando SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, scheduling: Scheduling) -> Scheduling:
        model = SchedulingModel.from_entity(scheduling)
        self._session.add(model)
        await self._session.flush()
        
        # The model is now in the session, but relationships (student/instructor) 
        # might not be loaded. However, the use cases usually only need the ID 
        # or the caller already has the info. But to_entity() NEEDS them.
        # Instead of a full get_by_id (which is SELECT * + multiple JOINs), 
        # we can just return the entity if we are sure the relationships are there, 
        # or just keep it as is if it's the safest way to avoid MissingGreenlet.
        # Actually, if we want to optimize, we should return the entity directly if possible.
        # For 'create', it's often better to just fetch it once to be safe.
        # But for 'update', we ALREADY fetched it with joinedload.
        created = await self.get_by_id(model.id)
        return created or model.to_entity()

    async def get_by_id(self, scheduling_id: UUID) -> Scheduling | None:
        stmt = (
            select(SchedulingModel)
            .where(SchedulingModel.id == scheduling_id)
            .options(
                joinedload(SchedulingModel.student).load_only(UserModel.id, UserModel.full_name),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile)
                ),
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
                joinedload(SchedulingModel.student).load_only(UserModel.id, UserModel.full_name),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile)
                ),
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
        model.scheduled_datetime = scheduling.scheduled_datetime
        model.rescheduled_datetime = scheduling.rescheduled_datetime
        model.duration_minutes = scheduling.duration_minutes
        model.price = scheduling.price
        model.status = scheduling.status
        model.cancellation_reason = scheduling.cancellation_reason
        model.cancelled_by = scheduling.cancelled_by
        model.cancelled_at = scheduling.cancelled_at
        model.completed_at = scheduling.completed_at
        model.started_at = scheduling.started_at
        model.student_confirmed_at = scheduling.student_confirmed_at
        model.rescheduled_by = scheduling.rescheduled_by
        model.updated_at = scheduling.updated_at

        # Commit da transação
        await self._session.flush()
        
        # The model was already loaded with joinedload options in the first select.
        # After flush(), we don't need to fetch it again.
        return model.to_entity()

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
        payment_status_filter: str | None = None,
    ) -> Sequence[Scheduling]:
        from src.infrastructure.db.models.payment_model import PaymentModel
        from src.domain.entities.payment_status import PaymentStatus

        # Para a tela "Minhas Aulas" (sem filtro de status), ordenamos ASC para mostrar as próximas aulas.
        # Para o "Histórico" (com filtro de status), costuma-se usar DESC para mostrar as mais recentes primeiro.
        order = SchedulingModel.scheduled_datetime.asc() if status is None else SchedulingModel.scheduled_datetime.desc()

        stmt = (
            select(SchedulingModel)
            .outerjoin(SchedulingModel.payment)
            .where(SchedulingModel.student_id == student_id)
            .order_by(order)
            .limit(limit)
            .offset(offset)
            .options(
                contains_eager(SchedulingModel.payment),
                joinedload(SchedulingModel.student).load_only(UserModel.id, UserModel.full_name),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile)
                ),
                joinedload(SchedulingModel.review)
            )
        )

        if status:
            if isinstance(status, (list, tuple)):
                stmt = stmt.where(SchedulingModel.status.in_(status))
            else:
                stmt = stmt.where(SchedulingModel.status == status)

        # Filtro por payment_status
        if payment_status_filter == "pending":
            # Carrinho: agendamentos com pagamento PENDING ou PROCESSING, ou sem pagamento
            stmt = stmt.where(
                or_(
                    PaymentModel.id.is_(None),
                    PaymentModel.status.in_([PaymentStatus.PENDING, PaymentStatus.PROCESSING]),
                ),
                SchedulingModel.status.notin_([SchedulingStatus.CANCELLED, SchedulingStatus.COMPLETED])
            )
        elif payment_status_filter == "completed":
            # Aulas com pagamento confirmado
            stmt = stmt.where(PaymentModel.status == PaymentStatus.COMPLETED)
        elif payment_status_filter == "none":
            # Agendamentos sem nenhum pagamento associado
            stmt = stmt.where(PaymentModel.id.is_(None))

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.unique().scalars().all()]

    async def count_by_student(
        self,
        student_id: UUID,
        status: SchedulingStatus | Sequence[SchedulingStatus] | None = None,
        payment_status_filter: str | None = None,
    ) -> int:
        from src.infrastructure.db.models.payment_model import PaymentModel
        from src.domain.entities.payment_status import PaymentStatus

        stmt = select(func.count()).select_from(SchedulingModel).where(SchedulingModel.student_id == student_id)

        if payment_status_filter:
            stmt = stmt.outerjoin(PaymentModel, PaymentModel.scheduling_id == SchedulingModel.id)

        if status:
            if isinstance(status, (list, tuple)):
                stmt = stmt.where(SchedulingModel.status.in_(status))
            else:
                stmt = stmt.where(SchedulingModel.status == status)

        if payment_status_filter == "pending":
            stmt = stmt.where(
                or_(
                    PaymentModel.id.is_(None),
                    PaymentModel.status.in_([PaymentStatus.PENDING, PaymentStatus.PROCESSING]),
                ),
                SchedulingModel.status.notin_([SchedulingStatus.CANCELLED, SchedulingStatus.COMPLETED])
            )
        elif payment_status_filter == "completed":
            stmt = stmt.where(PaymentModel.status == PaymentStatus.COMPLETED)
        elif payment_status_filter == "none":
            stmt = stmt.where(PaymentModel.id.is_(None))

        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def list_by_instructor(
        self,
        instructor_id: UUID,
        status: SchedulingStatus | Sequence[SchedulingStatus] | None = None,
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
                joinedload(SchedulingModel.student).load_only(UserModel.id, UserModel.full_name),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile)
                ),
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

    async def get_next_instructor_scheduling(
        self,
        instructor_id: UUID,
    ) -> Scheduling | None:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        stmt = (
            select(SchedulingModel)
            .where(
                SchedulingModel.instructor_id == instructor_id,
                SchedulingModel.scheduled_datetime >= now,
                SchedulingModel.status.notin_([SchedulingStatus.CANCELLED, SchedulingStatus.COMPLETED])
            )
            .order_by(SchedulingModel.scheduled_datetime.asc())
            .limit(1)
            .options(
                joinedload(SchedulingModel.student).load_only(UserModel.id, UserModel.full_name),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile)
                ),
                joinedload(SchedulingModel.review)
            )
        )

        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_next_student_scheduling(
        self,
        student_id: UUID,
    ) -> Scheduling | None:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        stmt = (
            select(SchedulingModel)
            .where(
                SchedulingModel.student_id == student_id,
                SchedulingModel.scheduled_datetime >= now,
                SchedulingModel.status.notin_([SchedulingStatus.CANCELLED, SchedulingStatus.COMPLETED])
            )
            .order_by(SchedulingModel.scheduled_datetime.asc())
            .limit(1)
            .options(
                joinedload(SchedulingModel.student).load_only(UserModel.id, UserModel.full_name),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile)
                ),
                joinedload(SchedulingModel.review)
            )
        )

        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        return model.to_entity() if model else None

    async def count_by_instructor(
        self, 
        instructor_id: UUID, 
        status: SchedulingStatus | Sequence[SchedulingStatus] | None = None
    ) -> int:
        stmt = select(func.count()).select_from(SchedulingModel).where(SchedulingModel.instructor_id == instructor_id)

        if status:
            if isinstance(status, (list, tuple, Sequence)):
                stmt = stmt.where(SchedulingModel.status.in_(status))
            else:
                stmt = stmt.where(SchedulingModel.status == status)

        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    async def check_conflict(
        self, 
        instructor_id: UUID, 
        scheduled_datetime: "datetime", 
        duration_minutes: int,
        exclude_scheduling_id: UUID | None = None
    ) -> bool:
        """
        Verifica se existe conflito de horário para o instrutor.
        Conflito ocorre se um agendamento existente se sobrepõe ao novo horário.
        Ignora agendamentos cancelados.
        """
        from datetime import timedelta, timezone

        # Garantir que scheduled_datetime é aware (UTC se naive)
        if scheduled_datetime.tzinfo is None:
            scheduled_datetime = scheduled_datetime.replace(tzinfo=timezone.utc)

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

        if exclude_scheduling_id:
            stmt = stmt.where(SchedulingModel.id != exclude_scheduling_id)
        
        # Nota: `func.make_interval` é específico do Postgres.
        # Alternativa portátil seria calcular end_time na aplicação ou persistir end_time no banco.
        # Como usamos Postgres + PostGIS, make_interval é aceitável.
        # Mas para garantir robustez, vamos usar datetime puro se possível, mas no 'where' precisamos de expressão SQL.
        # Outra opção: adicionar coluna `end_datetime` no modelo para facilitar queries, mas vamos usar aritmética de data por enquanto.

        result = await self._session.execute(stmt)
        return result.first() is not None

    async def list_by_student_and_instructor(
        self,
        student_id: UUID,
        instructor_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Scheduling]:
        stmt = (
            select(SchedulingModel)
            .where(
                and_(
                    SchedulingModel.student_id == student_id,
                    SchedulingModel.instructor_id == instructor_id,
                )
            )
            .order_by(SchedulingModel.scheduled_datetime.desc())
            .limit(limit)
            .offset(offset)
            .options(
                joinedload(SchedulingModel.student).load_only(UserModel.id, UserModel.full_name),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile)
                ),
                joinedload(SchedulingModel.review),
            )
        )
        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.unique().scalars().all()]

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
                joinedload(SchedulingModel.student).load_only(UserModel.id, UserModel.full_name),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile)
                ),
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
                SchedulingModel.status.notin_([SchedulingStatus.CANCELLED, SchedulingStatus.COMPLETED]),
            )
            .distinct()
            .order_by(func.date(local_ts))
        )

        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_overdue_confirmed(
        self, hours_threshold: int = 24
    ) -> list[Scheduling]:
        """
        Busca agendamentos confirmados cujo término excedeu hours_threshold
        e que o aluno não confirmou conclusão (student_confirmed_at IS NULL).
        """
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=hours_threshold)

        # end_datetime = scheduled_datetime + duration_minutes
        end_expr = SchedulingModel.scheduled_datetime + func.make_interval(
            0, 0, 0, 0, 0, SchedulingModel.duration_minutes
        )

        stmt = (
            select(SchedulingModel)
            .where(
                SchedulingModel.status == SchedulingStatus.CONFIRMED,
                SchedulingModel.student_confirmed_at.is_(None),
                end_expr <= cutoff,
            )
            .options(
                joinedload(SchedulingModel.student).load_only(
                    UserModel.id, UserModel.full_name
                ),
                joinedload(SchedulingModel.instructor).options(
                    load_only(UserModel.id, UserModel.full_name),
                    joinedload(UserModel.instructor_profile),
                ),
                joinedload(SchedulingModel.review),
            )
        )

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.unique().scalars().all()]

    async def get_expired_cart_items(
        self, 
        student_id: UUID | None = None,
        timeout_minutes: int = 12, 
        processing_timeout_minutes: int = 30
    ) -> list[Scheduling]:
        """
        Busca agendamentos no carrinho que expiraram o timeout.

        1. PENDING/sem pagamento: expiram em timeout_minutes (12).
        2. PROCESSING: expiram em processing_timeout_minutes (30).
        """
        from datetime import datetime, timedelta, timezone
        from src.infrastructure.db.models.payment_model import PaymentModel
        from src.domain.entities.payment_status import PaymentStatus

        now = datetime.now(timezone.utc)
        cutoff_pending = now - timedelta(minutes=timeout_minutes)
        cutoff_processing = now - timedelta(minutes=processing_timeout_minutes)

        stmt = (
            select(SchedulingModel)
            .outerjoin(PaymentModel, PaymentModel.scheduling_id == SchedulingModel.id)
            .where(
                SchedulingModel.status.in_([SchedulingStatus.PENDING, SchedulingStatus.CONFIRMED]),
                or_(
                    # Caso 1: Sem pagamento ou PENDING -> expira em 12min
                    and_(
                        SchedulingModel.created_at <= cutoff_pending,
                        or_(
                            PaymentModel.id.is_(None),
                            PaymentModel.status == PaymentStatus.PENDING,
                        ),
                    ),
                    # Caso 2: PROCESSING -> expira em 30min (proteção de checkout)
                    and_(
                        SchedulingModel.created_at <= cutoff_processing,
                        PaymentModel.status == PaymentStatus.PROCESSING,
                    ),
                ),
            )
        )

        if student_id:
            stmt = stmt.where(SchedulingModel.student_id == student_id)

        stmt = stmt.options(
            joinedload(SchedulingModel.student).load_only(
                UserModel.id, UserModel.full_name
            ),
            joinedload(SchedulingModel.instructor).options(
                load_only(UserModel.id, UserModel.full_name),
                joinedload(UserModel.instructor_profile),
            ),
            joinedload(SchedulingModel.review),
        )

        result = await self._session.execute(stmt)
        return [row.to_entity() for row in result.unique().scalars().all()]

