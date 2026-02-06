"""
Review Entity

Entidade de domínio representando uma avaliação de aula.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class Review:
    """
    Entidade de avaliação de aula.

    Attributes:
        scheduling_id: ID do agendamento avaliado.
        student_id: ID do aluno que avaliou.
        instructor_id: ID do instrutor avaliado.
        rating: Nota de 1 a 5.
        comment: Comentário opcional.
    """

    scheduling_id: UUID
    student_id: UUID
    instructor_id: UUID
    rating: int
    comment: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        if not (1 <= self.rating <= 5):
            raise ValueError("A nota deve estar entre 1 e 5")
        if self.student_id == self.instructor_id:
            raise ValueError("O avaliador e o avaliado devem ser diferentes")
