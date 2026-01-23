"""
Domain Layer

Camada de domínio contendo entidades puras, interfaces (protocols) e exceções.
Não deve ter dependências de frameworks ou bibliotecas externas.
"""

from .entities import RefreshToken, User, UserType
from .exceptions import (
    DomainException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
    TokenRevokedException,
    UserAlreadyExistsException,
    UserInactiveException,
    UserNotFoundException,
)
from .interfaces import IAuthService, ITokenRepository, IUserRepository

__all__ = [
    # Entities
    "User",
    "UserType",
    "RefreshToken",
    # Interfaces
    "IUserRepository",
    "ITokenRepository",
    "IAuthService",
    # Exceptions
    "DomainException",
    "UserNotFoundException",
    "UserAlreadyExistsException",
    "InvalidCredentialsException",
    "UserInactiveException",
    "TokenExpiredException",
    "TokenRevokedException",
    "InvalidTokenException",
]
