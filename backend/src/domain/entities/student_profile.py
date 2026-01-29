"""
StudentProfile Entity

Entidade de domínio representando o perfil de um aluno.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


class LearningStage:
    """Estágios de aprendizado do aluno."""

    BEGINNER = "beginner"  # Nunca dirigiu
    BASIC = "basic"  # Conhece o básico
    INTERMEDIATE = "intermediate"  # Praticando para prova
    ADVANCED = "advanced"  # Reciclagem/aprimoramento


@dataclass
class StudentProfile:
    """
    Perfil de aluno de direção.

    Contém informações sobre objetivos e preferências de aprendizado.

    Attributes:
        user_id: ID do usuário associado (FK para User).
        preferred_schedule: Horários preferidos (ex: 'manhã', 'tarde', 'noite').
        license_category_goal: Categoria de CNH desejada (ex: 'B', 'AB').
        learning_stage: Estágio atual de aprendizado.
        notes: Observações adicionais do aluno.
        total_lessons: Total de aulas realizadas.
    """

    user_id: UUID
    preferred_schedule: str = ""
    license_category_goal: str = "B"
    learning_stage: str = LearningStage.BEGINNER
    notes: str = ""
    total_lessons: int = 0
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        valid_stages = [
            LearningStage.BEGINNER,
            LearningStage.BASIC,
            LearningStage.INTERMEDIATE,
            LearningStage.ADVANCED,
        ]
        if self.learning_stage not in valid_stages:
            raise ValueError(f"Estágio de aprendizado inválido: {self.learning_stage}")
        if self.total_lessons < 0:
            raise ValueError("Total de aulas não pode ser negativo")

    def update_profile(
        self,
        preferred_schedule: str | None = None,
        license_category_goal: str | None = None,
        learning_stage: str | None = None,
        notes: str | None = None,
    ) -> None:
        """
        Atualiza informações do perfil.

        Args:
            preferred_schedule: Novos horários preferidos (opcional).
            license_category_goal: Nova categoria de CNH objetivo (opcional).
            learning_stage: Novo estágio de aprendizado (opcional).
            notes: Novas observações (opcional).
        """
        if preferred_schedule is not None:
            self.preferred_schedule = preferred_schedule
        if license_category_goal is not None:
            self.license_category_goal = license_category_goal
        if learning_stage is not None:
            valid_stages = [
                LearningStage.BEGINNER,
                LearningStage.BASIC,
                LearningStage.INTERMEDIATE,
                LearningStage.ADVANCED,
            ]
            if learning_stage not in valid_stages:
                raise ValueError(f"Estágio de aprendizado inválido: {learning_stage}")
            self.learning_stage = learning_stage
        if notes is not None:
            self.notes = notes

        self.updated_at = datetime.utcnow()

    def increment_lessons(self) -> None:
        """Incrementa o contador de aulas realizadas."""
        self.total_lessons += 1
        self.updated_at = datetime.utcnow()

    def advance_stage(self) -> None:
        """
        Avança para o próximo estágio de aprendizado.

        Raises:
            ValueError: Se já estiver no estágio máximo.
        """
        stages = [
            LearningStage.BEGINNER,
            LearningStage.BASIC,
            LearningStage.INTERMEDIATE,
            LearningStage.ADVANCED,
        ]
        current_index = stages.index(self.learning_stage)

        if current_index >= len(stages) - 1:
            raise ValueError("Aluno já está no estágio máximo de aprendizado")

        self.learning_stage = stages[current_index + 1]
        self.updated_at = datetime.utcnow()
