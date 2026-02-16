"""
Application Use Cases

Casos de uso que orquestram as regras de negócio.
"""

from .common.login_user import LoginUserUseCase
from .common.logout_user import LogoutUserUseCase
from .payment import (
    CalculateSplitUseCase,
    ConnectGatewayAccountUseCase,
    CreateCheckoutUseCase,
    GetInstructorEarningsUseCase,
    GetPaymentHistoryUseCase,
    HandlePaymentWebhookUseCase,
    ProcessRefundUseCase,
)
from .common.refresh_token import RefreshTokenUseCase
from .common.register_user import RegisterUserUseCase
from .common.reset_password import RequestPasswordResetUseCase, ResetPasswordUseCase
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
    # Payment Use Cases
    "CalculateSplitUseCase",
    "CreateCheckoutUseCase",
    "HandlePaymentWebhookUseCase",
    "ProcessRefundUseCase",
    "GetPaymentHistoryUseCase",
    "ConnectGatewayAccountUseCase",
    "GetInstructorEarningsUseCase",
]

