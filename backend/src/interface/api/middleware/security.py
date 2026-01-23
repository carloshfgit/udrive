"""
Security Headers Middleware

Middleware para adicionar headers de segurança a todas as respostas.
Conforme PROJECT_GUIDELINES.md.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.infrastructure.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware que adiciona headers de segurança a todas as respostas.

    Headers implementados:
        - X-Content-Type-Options: Previne MIME sniffing
        - X-Frame-Options: Previne clickjacking
        - X-XSS-Protection: Proteção XSS (legado, ainda útil)
        - Referrer-Policy: Controla informações de referrer
        - Strict-Transport-Security: HSTS (apenas em produção)
        - Content-Security-Policy: CSP básico (opcional)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Processa a requisição e adiciona headers de segurança na resposta."""
        response = await call_next(request)

        # Headers básicos de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissões de features do browser
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )

        # HSTS apenas em produção (requer HTTPS)
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return response
