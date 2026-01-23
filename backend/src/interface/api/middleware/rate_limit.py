"""
Rate Limiting Middleware

Configuração do slowapi para proteção contra abusos.
Limites conforme PROJECT_GUIDELINES.md.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Limiter global usando IP como chave
limiter = Limiter(key_func=get_remote_address)


# =============================================================================
# Limites pré-definidos (podem ser importados nos endpoints)
# =============================================================================

# Conforme PROJECT_GUIDELINES.md:
# - Login: 5 tentativas/min por IP
# - API geral: 100 req/min por usuário
# - Endpoints públicos: 30 req/min por IP

RATE_LIMIT_LOGIN = "5/minute"
RATE_LIMIT_PUBLIC = "30/minute"
RATE_LIMIT_AUTHENTICATED = "100/minute"


# =============================================================================
# Handler para quando o limite é excedido
# =============================================================================


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """
    Handler para quando o rate limit é excedido.

    Retorna 429 Too Many Requests com detalhes.
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Muitas requisições. Por favor, aguarde antes de tentar novamente.",
            "code": "RATE_LIMIT_EXCEEDED",
            "retry_after": str(exc.detail),
        },
        headers={"Retry-After": str(exc.detail)},
    )
