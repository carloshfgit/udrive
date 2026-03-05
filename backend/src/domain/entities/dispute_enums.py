"""
Dispute Enums

Enums para o sistema de disputas de aulas.
"""

from enum import Enum


class DisputeReason(str, Enum):
    """
    Motivos pré-definidos para abertura de disputa pelo aluno.

    Valores:
        NO_SHOW: Instrutor não compareceu à aula.
        VEHICLE_PROBLEM: Problemas mecânicos no veículo do instrutor.
        OTHER: Outro motivo (campo de texto livre obrigatório).
    """

    NO_SHOW = "no_show"
    """Instrutor não compareceu."""

    VEHICLE_PROBLEM = "vehicle_problem"
    """Problemas mecânicos no veículo."""

    OTHER = "other"
    """Outro motivo (requer descrição detalhada)."""


class DisputeStatus(str, Enum):
    """
    Estados do ciclo de vida de uma disputa.

    Fluxo de transição:
        OPEN -> UNDER_REVIEW -> RESOLVED
    """

    OPEN = "open"
    """Disputa recém-aberta, aguardando análise do suporte."""

    UNDER_REVIEW = "under_review"
    """Suporte está analisando a disputa."""

    RESOLVED = "resolved"
    """Disputa resolvida pelo suporte."""


class DisputeResolution(str, Enum):
    """
    Tipos de resolução possíveis para uma disputa.

    Valores:
        FAVOR_INSTRUCTOR: Serviço prestado, pagamento liberado (scheduling -> COMPLETED).
        FAVOR_STUDENT: Falha do instrutor, reembolso ao aluno (scheduling -> CANCELLED).
        RESCHEDULED: Acordo mútuo, nova data definida (scheduling -> CONFIRMED).
    """

    FAVOR_INSTRUCTOR = "favor_instructor"
    """Resolução a favor do instrutor — scheduling vai para COMPLETED."""

    FAVOR_STUDENT = "favor_student"
    """Resolução a favor do aluno — scheduling vai para CANCELLED + reembolso."""

    RESCHEDULED = "rescheduled"
    """Reagendamento mediado — scheduling volta para CONFIRMED com nova data."""
