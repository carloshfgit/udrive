"""
Scheduling Entity

Entidade de domínio representando um agendamento de aula.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from .scheduling_status import SchedulingStatus


@dataclass
class Scheduling:
    """
    Entidade de agendamento de aula entre aluno e instrutor.

    Attributes:
        student_id: ID do aluno (FK para User).
        instructor_id: ID do instrutor (FK para User).
        scheduled_datetime: Data e hora da aula.
        duration_minutes: Duração da aula em minutos.
        price: Valor da aula em BRL.
        status: Estado atual do agendamento.
        cancellation_reason: Motivo do cancelamento (se aplicável).
        cancelled_by: ID do usuário que cancelou (se aplicável).
        cancelled_at: Data/hora do cancelamento (se aplicável).
        completed_at: Data/hora da conclusão (se aplicável).
    """

    student_id: UUID
    instructor_id: UUID
    scheduled_datetime: datetime
    price: Decimal
    duration_minutes: int = 50
    status: SchedulingStatus = SchedulingStatus.PENDING
    cancellation_reason: str | None = None
    cancelled_by: UUID | None = None
    cancelled_at: datetime | None = None
    completed_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    student_name: str | None = None
    instructor_name: str | None = None

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        if self.price < 0:
            raise ValueError("Preço não pode ser negativo")
        if self.duration_minutes <= 0:
            raise ValueError("Duração deve ser maior que zero")
        if self.student_id == self.instructor_id:
            raise ValueError("Aluno e instrutor devem ser diferentes")

    def calculate_refund_percentage(self) -> int:
        """
        Calcula o percentual de reembolso baseado na regra de cancelamento.

        Regras:
            - > 24h antes da aula: 100% reembolso
            - < 24h antes da aula: 50% reembolso (multa de 50%)

        Returns:
            Percentual de reembolso (0-100).
        """
        now = datetime.now(timezone.utc)
        time_until_lesson = self.scheduled_datetime - now
        hours_until_lesson = time_until_lesson.total_seconds() / 3600

        if hours_until_lesson > 24:
            return 100
        return 50

    def can_cancel(self) -> bool:
        """
        Verifica se o agendamento pode ser cancelado.

        Returns:
            True se pode ser cancelado.
        """
        return self.status in (SchedulingStatus.PENDING, SchedulingStatus.CONFIRMED)

    def can_confirm(self) -> bool:
        """
        Verifica se o agendamento pode ser confirmado.

        Returns:
            True se pode ser confirmado (status == PENDING).
        """
        return self.status == SchedulingStatus.PENDING

    def can_complete(self) -> bool:
        """
        Verifica se o agendamento pode ser marcado como concluído.

        Returns:
            True se pode ser concluído (CONFIRMED e data já passou).
        """
        if self.status != SchedulingStatus.CONFIRMED:
            return False

        now = datetime.utcnow()
        lesson_end = self.scheduled_datetime + timedelta(minutes=self.duration_minutes)
        return now >= lesson_end

    def cancel(self, cancelled_by: UUID, reason: str | None = None) -> None:
        """
        Cancela o agendamento.

        Args:
            cancelled_by: ID do usuário que está cancelando.
            reason: Motivo do cancelamento.

        Raises:
            ValueError: Se o agendamento não pode ser cancelado.
        """
        if not self.can_cancel():
            raise ValueError(
                f"Agendamento não pode ser cancelado. Status atual: {self.status}"
            )

        self.status = SchedulingStatus.CANCELLED
        self.cancelled_by = cancelled_by
        self.cancellation_reason = reason
        self.cancelled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def confirm(self) -> None:
        """
        Confirma o agendamento (ação do instrutor).

        Raises:
            ValueError: Se o agendamento não pode ser confirmado.
        """
        if not self.can_confirm():
            raise ValueError(
                f"Agendamento não pode ser confirmado. Status atual: {self.status}"
            )

        self.status = SchedulingStatus.CONFIRMED
        self.updated_at = datetime.utcnow()

    def complete(self) -> None:
        """
        Marca o agendamento como concluído.

        Raises:
            ValueError: Se o agendamento não pode ser concluído.
        """
        if not self.can_complete():
            raise ValueError(
                f"Agendamento não pode ser concluído. Status: {self.status}"
            )

        self.status = SchedulingStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def is_pending(self) -> bool:
        """Verifica se está aguardando confirmação."""
        return self.status == SchedulingStatus.PENDING

    @property
    def is_confirmed(self) -> bool:
        """Verifica se está confirmado."""
        return self.status == SchedulingStatus.CONFIRMED

    @property
    def is_cancelled(self) -> bool:
        """Verifica se foi cancelado."""
        return self.status == SchedulingStatus.CANCELLED

    @property
    def is_completed(self) -> bool:
        """Verifica se foi concluído."""
        return self.status == SchedulingStatus.COMPLETED

    @property
    def lesson_end_datetime(self) -> datetime:
        """Retorna data/hora de término da aula."""
        return self.scheduled_datetime + timedelta(minutes=self.duration_minutes)
