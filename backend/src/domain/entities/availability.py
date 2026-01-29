"""
Availability Entity

Entidade de domínio representando a disponibilidade de um instrutor.
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from uuid import UUID, uuid4


@dataclass
class Availability:
    """
    Slot de disponibilidade do instrutor.

    Representa um período recorrente em que o instrutor está disponível
    para aulas (ex: Segunda-feira das 08:00 às 12:00).

    Attributes:
        instructor_id: ID do instrutor (FK para User).
        day_of_week: Dia da semana (0=Segunda a 6=Domingo).
        start_time: Hora de início do slot.
        end_time: Hora de término do slot.
        is_active: Se o slot está ativo e disponível para agendamentos.
    """

    instructor_id: UUID
    day_of_week: int
    start_time: time
    end_time: time
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    # Constantes para dias da semana
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    DAY_NAMES = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo",
    }

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        if not 0 <= self.day_of_week <= 6:
            raise ValueError("Dia da semana deve estar entre 0 (Segunda) e 6 (Domingo)")

        if self.start_time >= self.end_time:
            raise ValueError("Hora de início deve ser anterior à hora de término")

    def update(
        self,
        start_time: time | None = None,
        end_time: time | None = None,
        is_active: bool | None = None,
    ) -> None:
        """
        Atualiza os dados do slot de disponibilidade.

        Args:
            start_time: Nova hora de início (opcional).
            end_time: Nova hora de término (opcional).
            is_active: Novo estado ativo (opcional).

        Raises:
            ValueError: Se o intervalo de tempo for inválido.
        """
        new_start = start_time if start_time is not None else self.start_time
        new_end = end_time if end_time is not None else self.end_time

        if new_start >= new_end:
            raise ValueError("Hora de início deve ser anterior à hora de término")

        self.start_time = new_start
        self.end_time = new_end

        if is_active is not None:
            self.is_active = is_active

        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Desativa o slot de disponibilidade."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Ativa o slot de disponibilidade."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def contains_time(self, check_time: time) -> bool:
        """
        Verifica se um horário está dentro deste slot.

        Args:
            check_time: Horário a verificar.

        Returns:
            True se o horário está dentro do slot.
        """
        return self.start_time <= check_time < self.end_time

    def overlaps_with(self, other: "Availability") -> bool:
        """
        Verifica se este slot sobrepõe outro.

        Args:
            other: Outro slot de disponibilidade.

        Returns:
            True se há sobreposição.
        """
        if self.day_of_week != other.day_of_week:
            return False

        return (
            self.start_time < other.end_time and
            self.end_time > other.start_time
        )

    @property
    def day_name(self) -> str:
        """Retorna o nome do dia da semana em português."""
        return self.DAY_NAMES.get(self.day_of_week, "Desconhecido")

    @property
    def duration_minutes(self) -> int:
        """Calcula a duração do slot em minutos."""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return end_minutes - start_minutes

    def __repr__(self) -> str:
        """Representação legível do slot."""
        status = "ativo" if self.is_active else "inativo"
        return (
            f"Availability({self.day_name} "
            f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')} "
            f"[{status}])"
        )
