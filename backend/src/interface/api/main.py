"""
GoDrive API - Main Application

Ponto de entrada principal da API FastAPI.
"""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from src.infrastructure.config import settings
from src.interface.api.exceptions import EXCEPTION_HANDLERS
from src.interface.api.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from src.interface.api.middleware.security import SecurityHeadersMiddleware
from src.interface.api.routers import auth, health, instructors, students

# Configurar logging estruturado
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# =============================================================================
# Middlewares (ordem importa: último adicionado é executado primeiro)
# =============================================================================

# 1. Headers de segurança (executado por último na resposta)
app.add_middleware(SecurityHeadersMiddleware)

# 2. CORS (deve vir antes de outros middlewares)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Configurar Rate Limiter no estado do app
app.state.limiter = limiter

# =============================================================================
# Exception Handlers
# =============================================================================

# Registrar handlers para exceções de domínio
for exc_class, handler in EXCEPTION_HANDLERS.items():
    app.add_exception_handler(exc_class, handler)

# Handler para rate limit excedido
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# =============================================================================
# Routers
# =============================================================================

app.include_router(health.router, tags=["Health"])
app.include_router(auth.router)
app.include_router(instructors.router)
app.include_router(students.router)


# =============================================================================
# Eventos de Lifecycle
# =============================================================================


@app.on_event("startup")
async def startup_event() -> None:
    """Evento executado ao iniciar a aplicação."""
    logger.info(
        "application_startup",
        environment=settings.environment,
        debug=settings.debug,
        rate_limiting="enabled",
        security_headers="enabled",
    )


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Evento executado ao encerrar a aplicação."""
    logger.info("application_shutdown")
