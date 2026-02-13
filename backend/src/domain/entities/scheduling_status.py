"""
SchedulingStatus Enum

Enum para estados do agendamento de aulas.
"""

from enum import Enum


class SchedulingStatus(str, Enum):
    """
    Estados possíveis de um agendamento.

    Fluxo de transição:
        PENDING -> RESERVED -> CONFIRMED -> COMPLETED
        PENDING -> CONFIRMED -> COMPLETED
        PENDING -> CANCELLED
        RESERVED -> CANCELLED (expiração)
        CONFIRMED -> CANCELLED
    """

    PENDING = "pending"
    """Aguardando confirmação do instrutor."""

    RESERVED = "reserved"
    """Slot temporariamente reservado (aguardando checkout, expira em ~15min)."""

    CONFIRMED = "confirmed"
    """Confirmado pelo instrutor."""

    CANCELLED = "cancelled"
    """Cancelado (por aluno ou instrutor)."""

    COMPLETED = "completed"
    """Aula concluída."""

    RESCHEDULE_REQUESTED = "reschedule_requested"
    """Reagendamento solicitado pelo aluno, aguardando aprovação do instrutor."""
