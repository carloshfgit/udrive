"""
WebSocket Message Types

Constantes e schemas para o protocolo de mensagens WebSocket.
Define tipos para Chat e Agendamentos (Scheduling).
"""


# =============================================================================
# Client → Server (mensagens que o mobile envia)
# =============================================================================

class ClientMessageType:
    """Tipos de mensagens enviadas pelo cliente."""

    SEND_MESSAGE = "send_message"
    MARK_AS_READ = "mark_as_read"
    TYPING = "typing"
    PING = "ping"


# Tipos válidos que o cliente pode enviar
VALID_CLIENT_TYPES = {
    ClientMessageType.SEND_MESSAGE,
    ClientMessageType.MARK_AS_READ,
    ClientMessageType.TYPING,
    ClientMessageType.PING,
}


# =============================================================================
# Server → Client — Chat
# =============================================================================

class ServerChatMessageType:
    """Tipos de mensagens de chat enviadas pelo servidor."""

    NEW_MESSAGE = "new_message"
    MESSAGE_SENT = "message_sent"
    MESSAGES_READ = "messages_read"
    TYPING_INDICATOR = "typing_indicator"
    UNREAD_COUNT = "unread_count"
    PONG = "pong"
    ERROR = "error"


# =============================================================================
# Server → Client — Scheduling
# =============================================================================

class SchedulingEventType:
    """Tipos de eventos de agendamento enviados pelo servidor."""

    SCHEDULING_CREATED = "scheduling_created"
    SCHEDULING_CONFIRMED = "scheduling_confirmed"
    SCHEDULING_CANCELLED = "scheduling_cancelled"
    SCHEDULING_STARTED = "scheduling_started"
    SCHEDULING_COMPLETED = "scheduling_completed"
    RESCHEDULE_REQUESTED = "reschedule_requested"
    RESCHEDULE_RESPONDED = "reschedule_responded"


# Todos os tipos de scheduling (para validação/matching no mobile)
SCHEDULING_EVENT_TYPES = {
    SchedulingEventType.SCHEDULING_CREATED,
    SchedulingEventType.SCHEDULING_CONFIRMED,
    SchedulingEventType.SCHEDULING_CANCELLED,
    SchedulingEventType.SCHEDULING_STARTED,
    SchedulingEventType.SCHEDULING_COMPLETED,
    SchedulingEventType.RESCHEDULE_REQUESTED,
    SchedulingEventType.RESCHEDULE_RESPONDED,
}


# =============================================================================
# Error Codes
# =============================================================================

class WSErrorCode:
    """Códigos de erro para respostas de erro WebSocket."""

    INVALID_JSON = "INVALID_JSON"
    UNKNOWN_TYPE = "UNKNOWN_TYPE"
    MISSING_FIELDS = "MISSING_FIELDS"
    SEND_FAILED = "SEND_FAILED"
    READ_FAILED = "READ_FAILED"
    INVALID_UUID = "INVALID_UUID"
    RATE_LIMITED = "RATE_LIMITED"
