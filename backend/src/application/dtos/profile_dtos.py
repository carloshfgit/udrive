"""
Profile DTOs

Data Transfer Objects para operações com perfis de usuários.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


# === Input DTOs ===


@dataclass(frozen=True)
class UpdateInstructorProfileDTO:
    """DTO para criação/atualização de perfil de instrutor."""

    user_id: UUID
    bio: str | None = None
    vehicle_type: str | None = None
    license_category: str | None = None
    hourly_rate: Decimal | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_available: bool | None = None
    full_name: str | None = None
    phone: str | None = None
    cpf: str | None = None
    birth_date: date | None = None


@dataclass(frozen=True)
class UpdateStudentProfileDTO:
    """DTO para criação/atualização de perfil de aluno."""

    user_id: UUID
    preferred_schedule: str | None = None
    license_category_goal: str | None = None
    learning_stage: str | None = None
    notes: str | None = None
    phone: str | None = None
    cpf: str | None = None
    birth_date: date | None = None
    full_name: str | None = None


@dataclass(frozen=True)
class InstructorSearchDTO:
    """DTO para busca de instrutores por localização."""

    latitude: float
    longitude: float
    radius_km: float = 10.0
    only_available: bool = True
    limit: int = 50


@dataclass(frozen=True)
class UpdateLocationDTO:
    """DTO para atualização de localização."""

    user_id: UUID
    latitude: float
    longitude: float


# === Output DTOs ===


@dataclass
class LocationResponseDTO:
    """DTO de resposta para localização."""

    latitude: float
    longitude: float


@dataclass
class InstructorProfileResponseDTO:
    """DTO de resposta para perfil de instrutor."""

    id: UUID
    user_id: UUID
    bio: str
    vehicle_type: str
    license_category: str
    hourly_rate: Decimal
    rating: float
    total_reviews: int
    is_available: bool
    # Campos opcionais (podem não estar disponíveis em todas as buscas)
    full_name: str | None = None
    phone: str | None = None
    cpf: str | None = None
    birth_date: date | None = None
    location: LocationResponseDTO | None = None
    distance_km: float | None = None  # Preenchido em buscas por localização


@dataclass
class StudentProfileResponseDTO:
    """DTO de resposta para perfil de aluno."""

    id: UUID
    user_id: UUID
    preferred_schedule: str
    license_category_goal: str
    learning_stage: str
    notes: str
    total_lessons: int
    phone: str
    cpf: str
    birth_date: date | None
    full_name: str | None


@dataclass
class InstructorSearchResultDTO:
    """DTO de resposta para busca de instrutores."""

    instructors: list[InstructorProfileResponseDTO]
    total_count: int
    radius_km: float
    center_latitude: float
    center_longitude: float
