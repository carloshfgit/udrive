"""
Domain Interfaces

Contratos (Protocols) que definem comportamentos esperados.
Implementações concretas ficam na camada Infrastructure.
"""

from .auth_service import IAuthService
from .instructor_repository import IInstructorRepository
from .location_service import ILocationService
from .student_repository import IStudentRepository
from .token_repository import ITokenRepository
from .user_repository import IUserRepository

__all__ = [
    "IUserRepository",
    "ITokenRepository",
    "IAuthService",
    "IInstructorRepository",
    "IStudentRepository",
    "ILocationService",
]

