"""
Admin User Schemas

Schemas Pydantic para validação de requests e responses dos endpoints admin de usuários.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# =============================================================================
# Response Schemas
# =============================================================================


class UserAdminScheduling(BaseModel):
    """Schema para agendamento resumido."""

    id: UUID
    scheduled_datetime: datetime
    status: str
    price: float
    instructor_name: str | None = None
    student_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserAdminProfile(BaseModel):
    """Schema para detalhes de perfil."""

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

    model_config = ConfigDict(from_attributes=True)


class UserAdminResponse(BaseModel):
    """Schema de resposta para um usuário (visão admin)."""

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
    profile: UserAdminProfile | None = None
    recent_schedulings: list[UserAdminScheduling] = []

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema de resposta para lista paginada de usuários."""

    users: list[UserAdminResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool
