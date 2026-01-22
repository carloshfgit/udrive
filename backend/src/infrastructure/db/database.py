"""
Database Configuration

Configuração do SQLAlchemy 2.0+ com suporte assíncrono.
Pool de conexões otimizado conforme PROJECT_GUIDELINES.md.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.infrastructure.config import settings


class Base(DeclarativeBase):
    """Classe base para todos os models SQLAlchemy."""

    pass


# Engine assíncrono com pool de conexões otimizado
# pool_size=20, max_overflow=10 conforme PROJECT_GUIDELINES.md
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verifica conexões antes de usar
)

# Factory de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que fornece uma sessão de banco de dados.

    Yields:
        AsyncSession: Sessão do banco de dados.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Type alias para injeção de dependência
DbSession = Annotated[AsyncSession, Depends(get_db)]
