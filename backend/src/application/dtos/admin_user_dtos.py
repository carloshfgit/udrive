"""
Admin User DTOs

Data Transfer Objects para operações administrativas de usuários.
"""

from dataclasses import dataclass
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


@dataclass
class UserListResponseDTO:
    """DTO de resposta para lista paginada de usuários."""

    users: list[UserAdminResponseDTO]
    total_count: int
    limit: int
    offset: int
    has_more: bool
