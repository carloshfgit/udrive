"""
SchedulingStatus Enum

Enum para estados do agendamento de aulas.
"""

from enum import Enum


class SchedulingStatus(str, Enum):
    """
    Estados possíveis de um agendamento.

    Fluxo de transição:
        PENDING -> CONFIRMED -> COMPLETED
        PENDING -> CANCELLED
        CONFIRMED -> CANCELLED
    """

    PENDING = "pending"
    """Aguardando confirmação do instrutor."""

    CONFIRMED = "confirmed"
    """Confirmado pelo instrutor."""

    CANCELLED = "cancelled"
    """Cancelado (por aluno ou instrutor)."""

    COMPLETED = "completed"
    """Aula concluída."""

    RESCHEDULE_REQUESTED = "reschedule_requested"
    """Reagendamento solicitado pelo aluno, aguardando aprovação do instrutor."""
