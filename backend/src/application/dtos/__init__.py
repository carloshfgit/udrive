"""
Application DTOs Package

Data Transfer Objects para operações da camada de aplicação.
"""

from .auth_dtos import LoginDTO, RegisterUserDTO, TokenPairDTO
from .payment_dtos import (
    ConnectStripeAccountDTO,
    GetPaymentHistoryDTO,
    InstructorEarningsDTO,
    PaymentHistoryResponseDTO,
    PaymentResponseDTO,
    ProcessPaymentDTO,
    ProcessRefundDTO,
    RefundResultDTO,
    SplitCalculationDTO,
    StripeConnectResponseDTO,
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
    "ProcessPaymentDTO",
    "ProcessRefundDTO",
    "GetPaymentHistoryDTO",
    "ConnectStripeAccountDTO",
    "SplitCalculationDTO",
    "PaymentResponseDTO",
    "RefundResultDTO",
    "PaymentHistoryResponseDTO",
    "StripeConnectResponseDTO",
    "InstructorEarningsDTO",
]

