"""
Authentication DTOs

Data Transfer Objects para desacoplar camadas nas operações de autenticação.
"""

from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.user_type import UserType


@dataclass(frozen=True)
class RegisterUserDTO:
    """Dados de entrada para registro de usuário."""

    email: str
    password: str
    full_name: str
    user_type: UserType


@dataclass(frozen=True)
class LoginDTO:
    """Dados de entrada para login."""

    email: str
    password: str


@dataclass(frozen=True)
class TokenPairDTO:
    """Par de tokens retornado após autenticação."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass(frozen=True)
class RefreshTokenDTO:
    """Dados de entrada para refresh de token."""

    refresh_token: str


@dataclass(frozen=True)
class UserResponseDTO:
    """Dados de usuário para resposta (sem senha)."""

    id: UUID
    email: str
    full_name: str
    user_type: UserType
    is_active: bool
    is_verified: bool


@dataclass(frozen=True)
class ResetPasswordRequestDTO:
    """Dados para solicitar reset de senha."""

    email: str


@dataclass(frozen=True)
class ResetPasswordDTO:
    """Dados para executar reset de senha."""

    token: str
    new_password: str
