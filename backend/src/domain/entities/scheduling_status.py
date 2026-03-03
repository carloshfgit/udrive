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
        CONFIRMED -> DISPUTED (aluno abre disputa antes da auto-conclusão)
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
    """Reagendamento solicitado pelo aluno/instrutor, aguardando aprovação do instrutor/aluno."""

    DISPUTED = "disputed"
    """Aula em disputa pelo aluno. Impede auto-conclusão automática."""
