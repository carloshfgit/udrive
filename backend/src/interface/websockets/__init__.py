"""
Interface - WebSockets

Gerenciadores de conexão WebSocket para tempo real.
Inclui chat em tempo real e eventos de agendamento.
"""

from src.interface.websockets.auth import authenticate_websocket
from src.interface.websockets.chat_handler import ws_router
from src.interface.websockets.connection_manager import ConnectionManager, manager
from src.interface.websockets.event_dispatcher import (
    SchedulingEventDispatcher,
    get_event_dispatcher,
    init_event_dispatcher,
)
from src.interface.websockets.message_types import (
    ClientMessageType,
    SchedulingEventType,
    ServerChatMessageType,
    WSErrorCode,
)

__all__ = [
    "ClientMessageType",
    "ConnectionManager",
    "SchedulingEventDispatcher",
    "SchedulingEventType",
    "ServerChatMessageType",
    "WSErrorCode",
    "authenticate_websocket",
    "get_event_dispatcher",
    "init_event_dispatcher",
    "manager",
    "ws_router",
]
