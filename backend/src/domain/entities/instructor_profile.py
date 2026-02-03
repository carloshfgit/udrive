"""
InstructorProfile Entity

Entidade de domínio representando o perfil de um instrutor.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from .location import Location


@dataclass
class InstructorProfile:
    """
    Perfil de instrutor de direção.

    Contém informações profissionais, localização e disponibilidade.

    Attributes:
        user_id: ID do usuário associado (FK para User).
        bio: Descrição/biografia do instrutor.
        vehicle_type: Tipo de veículo (ex: 'Hatch', 'Sedan', 'SUV').
        license_category: Categoria da CNH (ex: 'B', 'AB', 'C').
        hourly_rate: Valor por hora de aula em BRL.
        location: Localização atual do instrutor.
        rating: Avaliação média (0.0 a 5.0).
        total_reviews: Total de avaliações recebidas.
        is_available: Se está disponível para novas aulas.
    """

    user_id: UUID
    bio: str = ""
    vehicle_type: str = ""
    license_category: str = "B"
    hourly_rate: Decimal = field(default_factory=lambda: Decimal("80.00"))
    location: Location | None = None
    rating: float = 0.0
    total_reviews: int = 0
    is_available: bool = True
    full_name: str | None = None
    stripe_account_id: str | None = None  # ID da conta Stripe Connect
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida campos após inicialização."""
        if self.hourly_rate < 0:
            raise ValueError("Valor por hora não pode ser negativo")
        if not 0 <= self.rating <= 5:
            raise ValueError("Rating deve estar entre 0 e 5")
        if self.total_reviews < 0:
            raise ValueError("Total de reviews não pode ser negativo")

    def update_location(self, new_location: Location) -> None:
        """
        Atualiza a localização do instrutor.

        Args:
            new_location: Nova localização.
        """
        self.location = new_location
        self.updated_at = datetime.utcnow()

    def set_availability(self, is_available: bool) -> None:
        """
        Define disponibilidade do instrutor.

        Args:
            is_available: True se disponível para aulas.
        """
        self.is_available = is_available
        self.updated_at = datetime.utcnow()

    def add_review(self, new_rating: float) -> None:
        """
        Adiciona uma nova avaliação e recalcula média.

        Args:
            new_rating: Nota da nova avaliação (0.0 a 5.0).

        Raises:
            ValueError: Se rating for inválido.
        """
        if not 0 <= new_rating <= 5:
            raise ValueError("Rating deve estar entre 0 e 5")

        # Recalcula média ponderada
        total_points = self.rating * self.total_reviews + new_rating
        self.total_reviews += 1
        self.rating = round(total_points / self.total_reviews, 2)
        self.updated_at = datetime.utcnow()

    def update_profile(
        self,
        bio: str | None = None,
        vehicle_type: str | None = None,
        license_category: str | None = None,
        hourly_rate: Decimal | None = None,
    ) -> None:
        """
        Atualiza informações do perfil.

        Args:
            bio: Nova biografia (opcional).
            vehicle_type: Novo tipo de veículo (opcional).
            license_category: Nova categoria de CNH (opcional).
            hourly_rate: Novo valor por hora (opcional).
        """
        if bio is not None:
            self.bio = bio
        if vehicle_type is not None:
            self.vehicle_type = vehicle_type
        if license_category is not None:
            self.license_category = license_category
        if hourly_rate is not None:
            if hourly_rate < 0:
                raise ValueError("Valor por hora não pode ser negativo")
            self.hourly_rate = hourly_rate

        self.updated_at = datetime.utcnow()

    @property
    def has_location(self) -> bool:
        """Verifica se o instrutor tem localização definida."""
        return self.location is not None
