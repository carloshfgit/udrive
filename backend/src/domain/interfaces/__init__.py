"""
Domain Interfaces

Contratos (Protocols) que definem comportamentos esperados.
Implementações concretas ficam na camada Infrastructure.
"""

from .auth_service import IAuthService
from .availability_repository import IAvailabilityRepository
from .instructor_repository import IInstructorRepository
from .location_service import ILocationService
from .payment_gateway import IPaymentGateway
from .payment_repository import IPaymentRepository
from .scheduling_repository import ISchedulingRepository
from .student_repository import IStudentRepository
from .token_repository import ITokenRepository
from .transaction_repository import ITransactionRepository
from .user_repository import IUserRepository

__all__ = [
    "IUserRepository",
    "ITokenRepository",
    "IAuthService",
    "IInstructorRepository",
    "IStudentRepository",
    "ILocationService",
    "ISchedulingRepository",
    "IAvailabilityRepository",
    "IPaymentRepository",
    "ITransactionRepository",
    "IPaymentGateway",
]

