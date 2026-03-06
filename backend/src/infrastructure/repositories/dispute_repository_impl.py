from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.domain.entities.dispute import Dispute
from src.domain.entities.dispute_enums import DisputeStatus
from src.domain.interfaces.dispute_repository import IDisputeRepository
from src.infrastructure.db.models.dispute_model import DisputeModel
from src.infrastructure.db.models.scheduling_model import SchedulingModel
from src.infrastructure.db.models.user_model import UserModel


class DisputeRepositoryImpl(IDisputeRepository):
    """
    Implementação do repositório de disputas usando SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, dispute: Dispute) -> Dispute:
        """Cria uma nova disputa."""
        model = DisputeModel.from_entity(dispute)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def get_by_id(self, dispute_id: UUID) -> Dispute | None:
        """Busca disputa por ID."""
        stmt = select(DisputeModel).where(DisputeModel.id == dispute_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def get_by_scheduling_id(self, scheduling_id: UUID) -> Dispute | None:
        """Busca disputa pelo ID do agendamento associado."""
        stmt = select(DisputeModel).where(
            DisputeModel.scheduling_id == scheduling_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_entity() if model else None

    async def update(self, dispute: Dispute) -> Dispute:
        """Atualiza uma disputa existente."""
        stmt = select(DisputeModel).where(DisputeModel.id == dispute.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Disputa não encontrada: {dispute.id}")

        # Atualizar campos
        model.status = dispute.status.value
        model.resolution = dispute.resolution.value if dispute.resolution else None
        model.resolution_notes = dispute.resolution_notes
        model.refund_type = dispute.refund_type
        model.resolved_by = dispute.resolved_by
        model.resolved_at = dispute.resolved_at
        model.updated_at = dispute.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_entity()

    async def list_by_status(
        self,
        status: DisputeStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Dispute]:
        """Lista disputas, opcionalmente filtradas por status."""
        stmt = select(DisputeModel).order_by(DisputeModel.created_at.desc())

        if status is not None:
            stmt = stmt.where(DisputeModel.status == status.value)

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [model.to_entity() for model in models]

    async def list_enriched(
        self,
        status: DisputeStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[tuple[Dispute, str, str, datetime]]:
        """Lista disputas enriquecidas com nomes e data do agendamento."""
        student = aliased(UserModel)
        instructor = aliased(UserModel)

        stmt = (
            select(
                DisputeModel,
                student.full_name.label("student_name"),
                instructor.full_name.label("instructor_name"),
                SchedulingModel.scheduled_datetime,
            )
            .join(SchedulingModel, DisputeModel.scheduling_id == SchedulingModel.id)
            .join(student, SchedulingModel.student_id == student.id)
            .join(instructor, SchedulingModel.instructor_id == instructor.id)
            .order_by(DisputeModel.created_at.desc())
        )

        if status is not None:
            stmt = stmt.where(DisputeModel.status == status.value)

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            (row[0].to_entity(), row[1], row[2], row[3])
            for row in rows
        ]

    async def get_enriched_by_id(
        self,
        dispute_id: UUID,
    ) -> tuple[Dispute, str, str, datetime] | None:
        """Busca uma disputa enriquecida por ID."""
        student = aliased(UserModel)
        instructor = aliased(UserModel)

        stmt = (
            select(
                DisputeModel,
                student.full_name.label("student_name"),
                instructor.full_name.label("instructor_name"),
                SchedulingModel.scheduled_datetime,
            )
            .join(SchedulingModel, DisputeModel.scheduling_id == SchedulingModel.id)
            .join(student, SchedulingModel.student_id == student.id)
            .join(instructor, SchedulingModel.instructor_id == instructor.id)
            .where(DisputeModel.id == dispute_id)
        )

        result = await self._session.execute(stmt)
        row = result.first()

        if row is None:
            return None

        return (row[0].to_entity(), row[1], row[2], row[3])

    async def count_by_status(
        self,
        status: DisputeStatus | None = None,
    ) -> int:
        """Conta disputas, opcionalmente filtradas por status."""
        stmt = select(func.count(DisputeModel.id))

        if status is not None:
            stmt = stmt.where(DisputeModel.status == status.value)

        result = await self._session.execute(stmt)
        return result.scalar_one()
