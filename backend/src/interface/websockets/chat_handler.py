"""
WebSocket Chat Handler

Endpoint WebSocket para comunicação em tempo real.
Gerencia o ciclo de vida da conexão: autenticação → loop de mensagens → desconexão.

Implementa handlers para:
- send_message: Envia mensagem via SendMessageUseCase + PubSub
- mark_as_read: Marca mensagens como lidas + notifica sender
- typing: Indicador de digitação (sem persistência)
- ping/pong: Keepalive
"""

import json
from uuid import UUID

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.application.dtos.chat_dtos import SendMessageDTO
from src.application.use_cases.chat.send_message_use_case import SendMessageUseCase
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.repositories.message_repository_impl import MessageRepositoryImpl
from src.infrastructure.repositories.scheduling_repository_impl import SchedulingRepositoryImpl
from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from src.interface.websockets.auth import authenticate_websocket
from src.interface.websockets.connection_manager import manager
from src.interface.websockets.message_types import (
    ClientMessageType,
    ServerChatMessageType,
    WSErrorCode,
)

logger = structlog.get_logger()

ws_router = APIRouter()

# Referência ao serviço de PubSub (injetado em startup)
_pubsub_service = None


def set_pubsub_service(pubsub) -> None:
    """Configura o serviço de PubSub para uso no handler."""
    global _pubsub_service
    _pubsub_service = pubsub


def get_pubsub_service():
    """Retorna o serviço de PubSub configurado."""
    return _pubsub_service


# =============================================================================
# Message Handlers
# =============================================================================


async def handle_send_message(websocket: WebSocket, user_id: UUID, data: dict) -> None:
    """
    Handler para envio de mensagem.

    1. Valida campos obrigatórios
    2. Cria sessão DB e instancia repositórios
    3. Executa SendMessageUseCase (validação + persistência)
    4. Publica no Redis PubSub para o receiver
    5. Envia confirmação ao sender
    """
    receiver_id_str = data.get("receiver_id")
    content = data.get("content")

    if not receiver_id_str or not content:
        await websocket.send_json({
            "type": ServerChatMessageType.ERROR,
            "data": {
                "code": WSErrorCode.MISSING_FIELDS,
                "message": "Campos 'receiver_id' e 'content' são obrigatórios",
            },
        })
        return

    try:
        receiver_id = UUID(receiver_id_str)
    except (ValueError, TypeError):
        await websocket.send_json({
            "type": ServerChatMessageType.ERROR,
            "data": {
                "code": WSErrorCode.INVALID_UUID,
                "message": "receiver_id não é um UUID válido",
            },
        })
        return

    # Criar sessão DB para esta operação
    async with AsyncSessionLocal() as session:
        try:
            # Instanciar repositórios
            message_repo = MessageRepositoryImpl(session)
            scheduling_repo = SchedulingRepositoryImpl(session)
            user_repo = UserRepositoryImpl(session)

            # Executar use case
            use_case = SendMessageUseCase(
                message_repository=message_repo,
                scheduling_repository=scheduling_repo,
                user_repository=user_repo,
            )
            dto = SendMessageDTO(receiver_id=receiver_id, content=content)
            result = await use_case.execute(sender_id=user_id, dto=dto)

            await session.commit()

            # Serializar resposta
            message_data = {
                "id": str(result.id),
                "sender_id": str(result.sender_id),
                "receiver_id": str(result.receiver_id),
                "content": result.content,
                "timestamp": result.timestamp.isoformat(),
                "is_read": result.is_read,
            }

            # Enviar confirmação ao sender
            await websocket.send_json({
                "type": ServerChatMessageType.MESSAGE_SENT,
                "data": message_data,
            })

            # Publicar no Redis PubSub para o receiver
            pubsub = get_pubsub_service()
            if pubsub:
                await pubsub.publish(
                    f"user:{receiver_id}",
                    {"type": ServerChatMessageType.NEW_MESSAGE, "data": message_data},
                )

            logger.info(
                "ws_message_sent",
                sender_id=str(user_id),
                receiver_id=str(receiver_id),
                message_id=str(result.id),
            )

        except Exception as e:
            await session.rollback()
            error_message = str(e)
            logger.error(
                "ws_send_message_error",
                user_id=str(user_id),
                error=error_message,
            )
            await websocket.send_json({
                "type": ServerChatMessageType.ERROR,
                "data": {
                    "code": WSErrorCode.SEND_FAILED,
                    "message": error_message,
                },
            })


async def handle_mark_as_read(websocket: WebSocket, user_id: UUID, data: dict) -> None:
    """
    Handler para marcar mensagens como lidas.

    1. Valida lista de IDs
    2. Marca no banco
    3. Notifica o sender original via PubSub
    """
    message_ids_raw = data.get("message_ids", [])

    if not message_ids_raw or not isinstance(message_ids_raw, list):
        await websocket.send_json({
            "type": ServerChatMessageType.ERROR,
            "data": {
                "code": WSErrorCode.MISSING_FIELDS,
                "message": "Campo 'message_ids' (lista) é obrigatório",
            },
        })
        return

    try:
        message_ids = [UUID(mid) for mid in message_ids_raw]
    except (ValueError, TypeError):
        await websocket.send_json({
            "type": ServerChatMessageType.ERROR,
            "data": {
                "code": WSErrorCode.INVALID_UUID,
                "message": "Um ou mais message_ids não são UUIDs válidos",
            },
        })
        return

    async with AsyncSessionLocal() as session:
        try:
            message_repo = MessageRepositoryImpl(session)
            await message_repo.mark_as_read(message_ids)
            await session.commit()

            # Buscar o sender_id da primeira mensagem para notificá-lo
            sender_id = data.get("sender_id")
            if sender_id:
                pubsub = get_pubsub_service()
                if pubsub:
                    await pubsub.publish(
                        f"user:{sender_id}",
                        {
                            "type": ServerChatMessageType.MESSAGES_READ,
                            "data": {
                                "message_ids": [str(mid) for mid in message_ids],
                                "read_by": str(user_id),
                            },
                        },
                    )

            # Enviar contagem atualizada de não lidas ao leitor
            unread_count = await message_repo.count_total_unread(user_id)
            await websocket.send_json({
                "type": ServerChatMessageType.UNREAD_COUNT,
                "data": {"count": unread_count},
            })

            logger.info(
                "ws_messages_marked_read",
                user_id=str(user_id),
                count=len(message_ids),
            )

        except Exception as e:
            await session.rollback()
            logger.error(
                "ws_mark_as_read_error",
                user_id=str(user_id),
                error=str(e),
            )
            await websocket.send_json({
                "type": ServerChatMessageType.ERROR,
                "data": {
                    "code": WSErrorCode.READ_FAILED,
                    "message": str(e),
                },
            })


async def handle_typing(user_id: UUID, data: dict) -> None:
    """
    Handler para indicador de digitação.

    Publica indicador via PubSub para o receiver (sem persistir).
    """
    receiver_id_str = data.get("receiver_id")
    if not receiver_id_str:
        return  # Silenciosamente ignora — typing não precisa de resposta de erro

    try:
        receiver_id = UUID(receiver_id_str)
    except (ValueError, TypeError):
        return

    pubsub = get_pubsub_service()
    if pubsub:
        await pubsub.publish(
            f"user:{receiver_id}",
            {
                "type": ServerChatMessageType.TYPING_INDICATOR,
                "data": {"user_id": str(user_id)},
            },
        )


# =============================================================================
# Main WebSocket Endpoint
# =============================================================================


@ws_router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket) -> None:
    """
    Endpoint principal de WebSocket para chat em tempo real.

    Fluxo:
    1. Extrai token da query string
    2. Autentica via JWT
    3. Aceita conexão e registra no ConnectionManager
    4. Subscreve canal Redis PubSub do usuário
    5. Loop de recebimento/processamento de mensagens
    6. Ao desconectar: limpa recursos
    """
    # 1. Extrair token da query string
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Token não fornecido")
        return

    # 2. Autenticar
    payload = authenticate_websocket(token)
    if payload is None:
        await websocket.close(code=1008, reason="Autenticação falhou")
        return

    user_id = payload["user_id"]
    pubsub = get_pubsub_service()

    # 3. Conectar
    await manager.connect(user_id, websocket)

    # 4. Subscrever no canal Redis PubSub do usuário
    if pubsub:
        async def on_pubsub_message(data: dict) -> None:
            """Callback: encaminha mensagem do Redis para o WebSocket."""
            await manager.send_to_user(user_id, data)

        await pubsub.subscribe(f"user:{user_id}", on_pubsub_message)

    try:
        # 5. Loop de recebimento de mensagens
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": ServerChatMessageType.ERROR,
                    "data": {
                        "code": WSErrorCode.INVALID_JSON,
                        "message": "Mensagem não é JSON válido",
                    },
                })
                continue

            msg_type = data.get("type")

            match msg_type:
                case ClientMessageType.PING:
                    await websocket.send_json({"type": ServerChatMessageType.PONG})

                case ClientMessageType.SEND_MESSAGE:
                    await handle_send_message(websocket, user_id, data)

                case ClientMessageType.MARK_AS_READ:
                    await handle_mark_as_read(websocket, user_id, data)

                case ClientMessageType.TYPING:
                    await handle_typing(user_id, data)

                case _:
                    await websocket.send_json({
                        "type": ServerChatMessageType.ERROR,
                        "data": {
                            "code": WSErrorCode.UNKNOWN_TYPE,
                            "message": f"Tipo de mensagem '{msg_type}' não reconhecido",
                        },
                    })

    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected", user_id=str(user_id))
    except Exception as e:
        logger.error("websocket_error", user_id=str(user_id), error=str(e))
    finally:
        # 6. Limpar recursos
        await manager.disconnect(user_id, websocket)
        if pubsub:
            await pubsub.unsubscribe(f"user:{user_id}")
