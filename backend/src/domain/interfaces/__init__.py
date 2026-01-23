"""
Domain Interfaces

Contratos (Protocols) que definem comportamentos esperados.
Implementações concretas ficam na camada Infrastructure.
"""

from .auth_service import IAuthService
from .token_repository import ITokenRepository
from .user_repository import IUserRepository

__all__ = [
    "IUserRepository",
    "ITokenRepository",
    "IAuthService",
]
