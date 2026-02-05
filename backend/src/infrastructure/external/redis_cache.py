"""
Redis Cache Service

Cliente Redis para cache de buscas de instrutores.
"""

import json
from typing import Any

import redis.asyncio as redis

from src.infrastructure.config import settings


class RedisCacheService:
    """
    Serviço de cache usando Redis.

    Implementa cache de resultados de busca de instrutores.
    """

    def __init__(self, redis_url: str | None = None) -> None:
        self._redis_url = redis_url or settings.redis_url
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        """Estabelece conexão com Redis."""
        if self._client is None:
            self._client = redis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

    async def disconnect(self) -> None:
        """Fecha conexão com Redis."""
        if self._client:
            await self._client.close()
            self._client = None

    async def get(self, key: str) -> str | None:
        """
        Obtém valor do cache.

        Args:
            key: Chave do cache.

        Returns:
            Valor em string ou None se não existir.
        """
        if self._client is None:
            await self.connect()
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl_seconds: int = 60) -> None:
        """
        Define valor no cache.

        Args:
            key: Chave do cache.
            value: Valor em string (use JSON para objetos).
            ttl_seconds: Tempo de vida em segundos (padrão 60).
        """
        if self._client is None:
            await self.connect()
        await self._client.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        """
        Remove valor do cache.

        Args:
            key: Chave do cache.
        """
        if self._client is None:
            await self.connect()
        await self._client.delete(key)

    async def delete_pattern(self, pattern: str) -> int:
        """
        Remove todas as chaves que correspondem ao padrão.

        Args:
            pattern: Padrão de chaves (ex: 'instructors:nearby:*').

        Returns:
            Número de chaves removidas.
        """
        if self._client is None:
            await self.connect()

        cursor = 0
        deleted_count = 0

        while True:
            cursor, keys = await self._client.scan(cursor, match=pattern, count=100)
            if keys:
                deleted_count += await self._client.delete(*keys)
            if cursor == 0:
                break

        return deleted_count

    async def get_json(self, key: str) -> dict[str, Any] | None:
        """
        Obtém valor JSON do cache.

        Args:
            key: Chave do cache.

        Returns:
            Dicionário ou None se não existir.
        """
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int = 60) -> None:
        """
        Define valor JSON no cache.

        Args:
            key: Chave do cache.
            value: Dicionário a ser serializado.
            ttl_seconds: Tempo de vida em segundos.
        """
        await self.set(key, json.dumps(value), ttl_seconds)


# Instância global (singleton)
cache_service = RedisCacheService()
