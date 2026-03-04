"""
Redis PubSub Service

Serviço de PubSub Redis para comunicação entre instâncias do backend.
Permite que mensagens WebSocket sejam entregues mesmo quando sender e receiver
estão conectados a instâncias diferentes (scaling horizontal).
"""

import asyncio
import json
from collections.abc import Callable, Coroutine
from typing import Any

import structlog
import redis.asyncio as redis

from src.infrastructure.config import settings

logger = structlog.get_logger()


class RedisPubSubService:
    """
    Serviço de PubSub Redis para comunicação em tempo real entre instâncias.

    Gerencia subscrições e publicações em canais Redis.
    Cada canal tem um callback associado que é chamado quando uma mensagem chega.
    """

    def __init__(self, redis_url: str | None = None) -> None:
        self._redis_url = redis_url or settings.redis_url
        self._client: redis.Redis | None = None
        self._pubsub: redis.client.PubSub | None = None
        self._listener_task: asyncio.Task | None = None
        self._callbacks: dict[str, list[Callable[[dict], Coroutine[Any, Any, None]]]] = {}
        self._running = False

    async def connect(self) -> None:
        """Estabelece conexão com Redis (listener é iniciado na primeira subscrição)."""
        if self._client is None:
            self._client = redis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            self._pubsub = self._client.pubsub()
            self._running = True
            logger.info("redis_pubsub_connected")

    async def disconnect(self) -> None:
        """Fecha conexão com Redis e para o listener."""
        self._running = False

        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            self._pubsub = None

        if self._client:
            await self._client.close()
            self._client = None

        self._callbacks.clear()
        logger.info("redis_pubsub_disconnected")

    async def publish(self, channel: str, message: dict) -> None:
        """
        Publica uma mensagem JSON em um canal Redis.

        Args:
            channel: Nome do canal (ex: "user:{user_id}").
            message: Dicionário a ser serializado como JSON.
        """
        if self._client is None:
            await self.connect()

        try:
            serialized = json.dumps(message, default=str)
            await self._client.publish(channel, serialized)
            logger.debug(
                "redis_pubsub_published",
                channel=channel,
                message_type=message.get("type"),
            )
        except Exception as e:
            logger.error(
                "redis_pubsub_publish_error",
                channel=channel,
                error=str(e),
            )

    async def subscribe(
        self,
        channel: str,
        callback: Callable[[dict], Coroutine[Any, Any, None]],
    ) -> None:
        """
        Subscreve em um canal Redis com um callback assíncrono.

        Suporta múltiplos callbacks por canal (multi-device).
        O callback é chamado toda vez que uma mensagem chega no canal.

        Args:
            channel: Nome do canal (ex: "user:{user_id}").
            callback: Função assíncrona que recebe o dict da mensagem.
        """
        if self._client is None:
            await self.connect()

        if channel not in self._callbacks:
            self._callbacks[channel] = []
            # Só subscreve no Redis na primeira vez para este canal
            await self._pubsub.subscribe(channel)

        self._callbacks[channel].append(callback)

        # Iniciar listener na primeira subscrição
        if self._listener_task is None or self._listener_task.done():
            self._listener_task = asyncio.create_task(self._listen())

        logger.info(
            "redis_pubsub_subscribed",
            channel=channel,
            total_callbacks=len(self._callbacks[channel]),
        )

    async def unsubscribe(
        self,
        channel: str,
        callback: Callable[[dict], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """
        Remove subscrição de um canal Redis.

        Se callback é fornecido, remove apenas esse callback específico.
        Se o canal ficar sem callbacks, desinscreve do Redis.
        Se callback é None, remove todos os callbacks do canal.

        Args:
            channel: Nome do canal.
            callback: Callback específico a remover (opcional).
        """
        if channel in self._callbacks:
            if callback is not None:
                # Remove apenas o callback específico
                try:
                    self._callbacks[channel].remove(callback)
                except ValueError:
                    pass  # Callback já foi removido

                # Se ainda há callbacks, não desinscreve do Redis
                if self._callbacks[channel]:
                    logger.info(
                        "redis_pubsub_callback_removed",
                        channel=channel,
                        remaining_callbacks=len(self._callbacks[channel]),
                    )
                    return

            # Remove o canal inteiro
            del self._callbacks[channel]

        if self._pubsub:
            await self._pubsub.unsubscribe(channel)

        logger.info("redis_pubsub_unsubscribed", channel=channel)

    async def _listen(self) -> None:
        """
        Loop interno que escuta mensagens do Redis PubSub.

        Processa mensagens recebidas e encaminha para os callbacks registrados.
        Roda como task asyncio em background.
        """
        while self._running:
            try:
                if self._pubsub is None:
                    await asyncio.sleep(1)
                    continue

                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )

                if message and message["type"] == "message":
                    channel = message["channel"]
                    callbacks = self._callbacks.get(channel, [])

                    if callbacks:
                        try:
                            data = json.loads(message["data"])
                        except json.JSONDecodeError:
                            logger.warning(
                                "redis_pubsub_invalid_json",
                                channel=channel,
                            )
                            continue

                        # Chamar todos os callbacks registrados para este canal
                        for cb in list(callbacks):  # list() para iterar sobre cópia
                            try:
                                await cb(data)
                            except Exception as e:
                                logger.error(
                                    "redis_pubsub_callback_error",
                                    channel=channel,
                                    error=str(e),
                                )
                else:
                    # Sem mensagem, sleep curto para não busy-loop
                    await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("redis_pubsub_listener_error", error=str(e))
                await asyncio.sleep(1)  # Backoff em caso de erro


# Instância global (singleton)
pubsub_service = RedisPubSubService()
