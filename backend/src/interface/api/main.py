"""
GoDrive API - Main Application

Ponto de entrada principal da API FastAPI.
"""

import asyncio

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from src.infrastructure.config import settings
from src.infrastructure.db.database import engine
from src.interface.admin import setup_admin
from src.interface.api.exceptions import EXCEPTION_HANDLERS
from src.interface.api.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from src.interface.api.middleware.security import SecurityHeadersMiddleware
from src.interface.api.routers import auth, health, instructor, shared, student
from src.interface.websockets.chat_handler import ws_router, set_pubsub_service
from src.interface.websockets.event_dispatcher import init_event_dispatcher
from src.infrastructure.external.redis_pubsub import pubsub_service
from src.application.tasks.cart_cleanup_task import cart_cleanup_loop
from src.infrastructure.db.database import AsyncSessionLocal

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

# 2. Session Middleware (necessário para o SQLAdmin)
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret_key)

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

# Routers organizados por tipo de usuário
app.include_router(student.router, prefix="/api/v1/student", tags=["Student"])
app.include_router(instructor.router, prefix="/api/v1/instructor", tags=["Instructor"])
app.include_router(shared.router, prefix="/api/v1/shared", tags=["Shared"])

# WebSocket routes
app.include_router(ws_router)


# =============================================================================
# Admin Interface
# =============================================================================

setup_admin(app, engine)


# =============================================================================
# Eventos de Lifecycle
# =============================================================================


@app.on_event("startup")
async def startup_event() -> None:
    """Evento executado ao iniciar a aplicação."""
    # Inicializar Redis PubSub para WebSockets
    await pubsub_service.connect()
    set_pubsub_service(pubsub_service)

    # Inicializar Event Dispatcher para eventos de agendamento em tempo real
    init_event_dispatcher(pubsub_service)

    # Iniciar background task de limpeza do carrinho
    app.state.cart_cleanup_task = asyncio.create_task(
        cart_cleanup_loop(AsyncSessionLocal)
    )

    logger.info(
        "application_startup",
        environment=settings.environment,
        debug=settings.debug,
        rate_limiting="enabled",
        security_headers="enabled",
        websockets="enabled",
        cart_cleanup="enabled",
    )


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Evento executado ao encerrar a aplicação."""
    # Cancelar background task de limpeza do carrinho
    if hasattr(app.state, 'cart_cleanup_task'):
        app.state.cart_cleanup_task.cancel()
        try:
            await app.state.cart_cleanup_task
        except asyncio.CancelledError:
            pass

    # Encerrar Redis PubSub
    await pubsub_service.disconnect()

    logger.info("application_shutdown")
