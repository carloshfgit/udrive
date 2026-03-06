"""
Admin User DTOs

Data Transfer Objects para operações administrativas de usuários.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID


# === Input DTOs ===


@dataclass(frozen=True)
class ListUsersDTO:
    """DTO para listagem de usuários com filtros."""

    user_type: str | None = None
    is_active: bool | None = None
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class SearchUsersDTO:
    """DTO para busca de usuários por texto."""

    query: str = ""
    limit: int = 20


@dataclass(frozen=True)
class ToggleUserStatusDTO:
    """DTO para ativar/desativar um usuário."""

    user_id: UUID = None  # type: ignore
    admin_id: UUID = None  # type: ignore


# === Output DTOs ===


@dataclass
class UserAdminSchedulingDTO:
    """DTO simplificado de agendamento para exibição em listas/detalhes."""

    id: UUID
    scheduled_datetime: datetime
    status: str
    price: float
    instructor_name: str | None = None
    student_name: str | None = None


@dataclass
class UserAdminProfileDTO:
    """DTO genérico para detalhes de perfil (student/instructor)."""

    # Campos de Instrutor
    bio: str | None = None
    vehicle_type: str | None = None
    license_category: str | None = None
    hourly_rate: float | None = None
    rating: float | None = None
    total_reviews: int | None = None

    # Campos de Aluno
    learning_stage: str | None = None
    license_category_goal: str | None = None
    total_lessons: int | None = None


@dataclass
class UserAdminResponseDTO:
    """DTO de resposta para um usuário (visão admin)."""

    id: UUID
    email: str
    full_name: str
    user_type: str
    is_active: bool
    is_verified: bool
    phone: str | None = None
    cpf: str | None = None
    birth_date: date | None = None
    biological_sex: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Novos campos para Etapa 2.2
    profile: UserAdminProfileDTO | None = None
    recent_schedulings: list[UserAdminSchedulingDTO] = field(default_factory=list)


@dataclass
class UserListResponseDTO:
    """DTO de resposta para lista paginada de usuários."""

    users: list[UserAdminResponseDTO]
    total_count: int
    limit: int
    offset: int
    has_more: bool
