"""
Application Use Cases

Casos de uso que orquestram as regras de negócio.
"""

from .login_user import LoginUserUseCase
from .logout_user import LogoutUserUseCase
from .refresh_token import RefreshTokenUseCase
from .register_user import RegisterUserUseCase
from .reset_password import RequestPasswordResetUseCase, ResetPasswordUseCase
from .scheduling import (
    CancelSchedulingUseCase,
    CompleteSchedulingUseCase,
    ConfirmSchedulingUseCase,
    CreateSchedulingUseCase,
    ListUserSchedulingsUseCase,
    ManageAvailabilityUseCase,
)

__all__ = [
    # Auth Use Cases
    "RegisterUserUseCase",
    "LoginUserUseCase",
    "RefreshTokenUseCase",
    "LogoutUserUseCase",
    "RequestPasswordResetUseCase",
    "ResetPasswordUseCase",
    # Scheduling Use Cases
    "CreateSchedulingUseCase",
    "CancelSchedulingUseCase",
    "ConfirmSchedulingUseCase",
    "CompleteSchedulingUseCase",
    "ListUserSchedulingsUseCase",
    "ManageAvailabilityUseCase",
]
