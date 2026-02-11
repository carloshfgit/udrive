"""
WebSocket Authentication

Autenticação JWT para conexões WebSocket.
O token é passado via query string já que WebSockets não suportam headers Authorization.
"""

import structlog

from src.domain.exceptions import InvalidTokenException, TokenExpiredException
from src.infrastructure.services.auth_service_impl import AuthServiceImpl

logger = structlog.get_logger()


def authenticate_websocket(token: str) -> dict | None:
    """
    Valida um token JWT extraído da query string de um WebSocket.

    Reutiliza a mesma lógica do AuthServiceImpl usada nos endpoints REST.

    Args:
        token: Token JWT em texto plano.

    Returns:
        dict com {user_id: UUID, user_type: UserType} se válido, ou None se inválido.
    """
    if not token:
        logger.warning("websocket_auth_failed", reason="Token vazio")
        return None

    auth_service = AuthServiceImpl()

    try:
        payload = auth_service.decode_access_token(token)
        logger.info(
            "websocket_auth_success",
            user_id=str(payload["user_id"]),
            user_type=payload["user_type"].value,
        )
        return payload
    except TokenExpiredException:
        logger.warning("websocket_auth_failed", reason="Token expirado")
        return None
    except InvalidTokenException:
        logger.warning("websocket_auth_failed", reason="Token inválido")
        return None
    except Exception as e:
        logger.error("websocket_auth_error", error=str(e))
        return None
