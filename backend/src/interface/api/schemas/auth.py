"""
Authentication Schemas

Esquemas Pydantic v2 para validação de requests e formatação de responses
nas operações de autenticação.
"""

from datetime import date
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class UserTypeEnum(str, Enum):
    """Tipos de usuário disponíveis no sistema."""

    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


# =============================================================================
# Request Schemas
# =============================================================================


class RegisterRequest(BaseModel):
    """Schema para cadastro de novo usuário."""

    email: str = Field(..., description="Email do usuário")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Senha (mínimo 8 caracteres)",
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome completo do usuário",
    )
    user_type: UserTypeEnum = Field(..., description="Tipo de usuário")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "joao@exemplo.com",
                    "password": "senhaSegura123",
                    "full_name": "João da Silva",
                    "user_type": "student",
                }
            ]
        }
    }


class LoginRequest(BaseModel):
    """Schema para login de usuário."""

    email: str = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "joao@exemplo.com",
                    "password": "senhaSegura123",
                }
            ]
        }
    }


class RefreshTokenRequest(BaseModel):
    """Schema para renovação de tokens."""

    refresh_token: str = Field(..., description="Refresh token atual")


class ForgotPasswordRequest(BaseModel):
    """Schema para solicitação de reset de senha."""

    email: str = Field(..., description="Email do usuário")


class ResetPasswordRequest(BaseModel):
    """Schema para execução do reset de senha."""

    token: str = Field(..., description="Token de reset recebido por email")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Nova senha (mínimo 8 caracteres)",
    )


# =============================================================================
# Response Schemas
# =============================================================================


class TokenResponse(BaseModel):
    """Schema de resposta com par de tokens."""

    access_token: str = Field(..., description="JWT de acesso")
    refresh_token: str = Field(..., description="Token para renovação")
    token_type: str = Field(default="bearer", description="Tipo do token")


class UserResponse(BaseModel):
    """Schema de resposta com dados do usuário (sem senha)."""

    id: UUID = Field(..., description="ID único do usuário")
    email: str = Field(..., description="Email do usuário")
    full_name: str = Field(..., description="Nome completo")
    user_type: UserTypeEnum = Field(..., description="Tipo de usuário")
    is_active: bool = Field(..., description="Se o usuário está ativo")
    is_verified: bool = Field(..., description="Se o email foi verificado")
    phone: str | None = Field(None, description="Telefone do usuário")
    cpf: str | None = Field(None, description="CPF do usuário")
    birth_date: date | None = Field(None, description="Data de nascimento")


class MessageResponse(BaseModel):
    """Schema de resposta genérica com mensagem."""

    message: str = Field(..., description="Mensagem de retorno")
