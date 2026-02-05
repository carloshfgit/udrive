"""
API Exception Handlers

Mapeamento de exceções de domínio para HTTP status codes.
Mantém a camada de interface isolada das regras de negócio.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    DomainException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
    TokenRevokedException,
    UserAlreadyExistsException,
    UserInactiveException,
    UserNotFoundException,
    InvalidSchedulingStateException,
    LessonNotFinishedException,
    SchedulingNotFoundException,
)


async def user_not_found_handler(
    request: Request, exc: UserNotFoundException
) -> JSONResponse:
    """Handler para usuário não encontrado → 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "code": exc.code},
    )


async def user_already_exists_handler(
    request: Request, exc: UserAlreadyExistsException
) -> JSONResponse:
    """Handler para usuário já existente → 409."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc), "code": exc.code},
    )


async def invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsException
) -> JSONResponse:
    """Handler para credenciais inválidas → 401."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc), "code": exc.code},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def user_inactive_handler(
    request: Request, exc: UserInactiveException
) -> JSONResponse:
    """Handler para usuário inativo → 403."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc), "code": exc.code},
    )


async def invalid_token_handler(
    request: Request, exc: InvalidTokenException
) -> JSONResponse:
    """Handler para token inválido → 401."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc), "code": exc.code},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def token_expired_handler(
    request: Request, exc: TokenExpiredException
) -> JSONResponse:
    """Handler para token expirado → 401."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc), "code": exc.code},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def token_revoked_handler(
    request: Request, exc: TokenRevokedException
) -> JSONResponse:
    """Handler para token revogado → 401."""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc), "code": exc.code},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    """Handler genérico para exceções de domínio → 400.
    Logamos o erro para visibilidade no terminal.
    """
    import structlog
    logger = structlog.get_logger()
    logger.warning(
        "domain_exception",
        path=request.url.path,
        exception=exc.__class__.__name__,
        message=str(exc),
        code=exc.code
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "code": exc.code},
    )


# Dicionário de mapeamento exceção → handler para registro fácil no app
EXCEPTION_HANDLERS = {
    UserNotFoundException: user_not_found_handler,
    UserAlreadyExistsException: user_already_exists_handler,
    InvalidCredentialsException: invalid_credentials_handler,
    UserInactiveException: user_inactive_handler,
    InvalidTokenException: invalid_token_handler,
    TokenExpiredException: token_expired_handler,
    TokenRevokedException: token_revoked_handler,
    LessonNotFinishedException: domain_exception_handler,
    InvalidSchedulingStateException: domain_exception_handler,
    SchedulingNotFoundException: domain_exception_handler,
    DomainException: domain_exception_handler,
}
