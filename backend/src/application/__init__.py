"""
Application Layer

Camada de aplicação contendo casos de uso e DTOs.
"""

from .dtos.auth_dtos import (
    LoginDTO,
    RefreshTokenDTO,
    RegisterUserDTO,
    ResetPasswordDTO,
    ResetPasswordRequestDTO,
    TokenPairDTO,
    UserResponseDTO,
)
from .use_cases import (
    LoginUserUseCase,
    LogoutUserUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)

__all__ = [
    # DTOs
    "RegisterUserDTO",
    "LoginDTO",
    "TokenPairDTO",
    "RefreshTokenDTO",
    "UserResponseDTO",
    "ResetPasswordRequestDTO",
    "ResetPasswordDTO",
    # Use Cases
    "RegisterUserUseCase",
    "LoginUserUseCase",
    "RefreshTokenUseCase",
    "LogoutUserUseCase",
    "RequestPasswordResetUseCase",
    "ResetPasswordUseCase",
]
