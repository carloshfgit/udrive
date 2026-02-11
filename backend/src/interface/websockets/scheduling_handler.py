"""
Scheduling Event Handler

Módulo complementar para subscrição de eventos de agendamento no WebSocket.
Os eventos de agendamento são server-push only — o mobile NÃO envia ações via WS.

Os eventos chegam via Redis PubSub no canal `user:{user_id}` e são
entregues ao cliente pelo callback `on_pubsub_message` no chat_handler.py.

Este módulo documenta os tipos de scheduling esperados e pode
adicionar lógica de processamento adicional no futuro (ex: logging, métricas).
"""

import structlog

from src.interface.websockets.message_types import SCHEDULING_EVENT_TYPES

logger = structlog.get_logger()


def is_scheduling_event(message_type: str) -> bool:
    """Verifica se o tipo de mensagem é um evento de agendamento."""
    return message_type in SCHEDULING_EVENT_TYPES


def log_scheduling_event(event_type: str, target_user_id: str) -> None:
    """Loga um evento de agendamento entregue via WebSocket."""
    logger.info(
        "scheduling_event_delivered",
        event_type=event_type,
        target_user_id=target_user_id,
    )
