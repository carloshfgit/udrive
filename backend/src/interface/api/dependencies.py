"""
API Dependencies

Sistema de injeção de dependências para desacoplar a API dos repositórios e serviços.
Usa o padrão de Dependency Injection do FastAPI.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.auth_service import IAuthService
from src.domain.interfaces.token_repository import ITokenRepository
from src.domain.interfaces.user_repository import IUserRepository
from src.infrastructure.db.database import get_db
from src.infrastructure.repositories.token_repository_impl import TokenRepositoryImpl
from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from src.infrastructure.services.auth_service_impl import AuthServiceImpl


# =============================================================================
# Database Session
# =============================================================================

DBSession = Annotated[AsyncSession, Depends(get_db)]


# =============================================================================
# Repository Dependencies
# =============================================================================


def get_user_repository(session: DBSession) -> IUserRepository:
    """
    Fornece uma instância do repositório de usuários.

    Args:
        session: Sessão do banco de dados injetada.

    Returns:
        IUserRepository: Implementação do repositório de usuários.
    """
    return UserRepositoryImpl(session)


def get_token_repository(session: DBSession) -> ITokenRepository:
    """
    Fornece uma instância do repositório de tokens.

    Args:
        session: Sessão do banco de dados injetada.

    Returns:
        ITokenRepository: Implementação do repositório de tokens.
    """
    return TokenRepositoryImpl(session)


# =============================================================================
# Service Dependencies
# =============================================================================


def get_auth_service() -> IAuthService:
    """
    Fornece uma instância do serviço de autenticação.

    Returns:
        IAuthService: Implementação do serviço de autenticação.
    """
    return AuthServiceImpl()


# =============================================================================
# Type Aliases para uso nos endpoints
# =============================================================================

UserRepo = Annotated[IUserRepository, Depends(get_user_repository)]
TokenRepo = Annotated[ITokenRepository, Depends(get_token_repository)]
AuthService = Annotated[IAuthService, Depends(get_auth_service)]
