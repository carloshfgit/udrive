"""
Application DTOs Package

Data Transfer Objects para operações da camada de aplicação.
"""

from .auth_dtos import LoginDTO, RegisterUserDTO, TokenPairDTO
from .payment_dtos import (
    CheckoutResponseDTO,
    ConnectGatewayAccountDTO,
    CreateCheckoutDTO,
    GetPaymentHistoryDTO,
    InstructorEarningsDTO,
    PaymentHistoryResponseDTO,
    PaymentResponseDTO,
    ProcessRefundDTO,
    RefundResultDTO,
    SplitCalculationDTO,
    GatewayConnectResponseDTO,
    WebhookNotificationDTO,
)
from .profile_dtos import (
    InstructorProfileResponseDTO,
    InstructorSearchDTO,
    InstructorSearchResultDTO,
    LocationResponseDTO,
    StudentProfileResponseDTO,
    UpdateInstructorProfileDTO,
    UpdateLocationDTO,
    UpdateStudentProfileDTO,
)
from .scheduling_dtos import (
    AvailabilityListResponseDTO,
    AvailabilityResponseDTO,
    CancellationResultDTO,
    CancelSchedulingDTO,
    CompleteSchedulingDTO,
    ConfirmSchedulingDTO,
    CreateAvailabilityDTO,
    CreateSchedulingDTO,
    DeleteAvailabilityDTO,
    ListSchedulingsDTO,
    SchedulingListResponseDTO,
    SchedulingResponseDTO,
    UpdateAvailabilityDTO,
)

__all__ = [
    # Auth DTOs
    "LoginDTO",
    "RegisterUserDTO",
    "TokenPairDTO",
    # Profile DTOs
    "UpdateInstructorProfileDTO",
    "UpdateStudentProfileDTO",
    "InstructorSearchDTO",
    "UpdateLocationDTO",
    "LocationResponseDTO",
    "InstructorProfileResponseDTO",
    "StudentProfileResponseDTO",
    "InstructorSearchResultDTO",
    # Scheduling DTOs
    "CreateSchedulingDTO",
    "CancelSchedulingDTO",
    "ConfirmSchedulingDTO",
    "CompleteSchedulingDTO",
    "ListSchedulingsDTO",
    "CreateAvailabilityDTO",
    "UpdateAvailabilityDTO",
    "DeleteAvailabilityDTO",
    "SchedulingResponseDTO",
    "CancellationResultDTO",
    "SchedulingListResponseDTO",
    "AvailabilityResponseDTO",
    "AvailabilityListResponseDTO",
    # Payment DTOs
    "CreateCheckoutDTO",
    "CheckoutResponseDTO",
    "WebhookNotificationDTO",
    "ProcessRefundDTO",
    "GetPaymentHistoryDTO",
    "ConnectGatewayAccountDTO",
    "SplitCalculationDTO",
    "PaymentResponseDTO",
    "RefundResultDTO",
    "PaymentHistoryResponseDTO",
    "GatewayConnectResponseDTO",
    "InstructorEarningsDTO",
]

