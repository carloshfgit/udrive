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

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema de resposta para lista paginada de usuários."""

    users: list[UserAdminResponse]
    total_count: int
    limit: int
    offset: int
    has_more: bool
