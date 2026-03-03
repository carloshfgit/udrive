"""
Notifications Router

Endpoints REST para o sistema de notificações.
Inclui listagem paginada, marcação como lida e gerenciamento de push tokens.
"""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from src.application.dtos.notification_dtos import (
    NotificationListDTO,
    NotificationSchema,
    UnreadCountSchema,
)
from src.application.services.notification_service import NotificationService
from src.interface.api.dependencies import CurrentUser, get_notification_service

logger = structlog.get_logger()

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Type alias para injeção do serviço (padrão do projeto)
NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]


# =============================================================================
# Leitura de notificações
# =============================================================================


@router.get("/", response_model=NotificationListDTO)
async def list_notifications(
    current_user: CurrentUser,
    service: NotificationServiceDep,
    limit: int = Query(50, ge=1, le=100, description="Quantidade de notificações a retornar"),
    offset: int = Query(0, ge=0, description="Paginação: posição de início"),
):
    """Lista notificações do usuário autenticado (mais recentes primeiro)."""
    notifications = await service.get_notifications(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    unread_count = await service.get_unread_count(user_id=current_user.id)

    return NotificationListDTO(
        notifications=[
            NotificationSchema(
                id=n.id,
                type=n.type.value,
                title=n.title,
                body=n.body,
                action_type=n.action_type.value if n.action_type else None,
                action_id=n.action_id,
                is_read=n.is_read,
                created_at=n.created_at,
                read_at=n.read_at,
            )
            for n in notifications
        ],
        unread_count=unread_count,
        total=len(notifications),
    )


@router.get("/unread-count", response_model=UnreadCountSchema)
async def get_unread_count(
    current_user: CurrentUser,
    service: NotificationServiceDep,
):
    """Retorna a contagem de notificações não lidas (para o badge do sininho)."""
    count = await service.get_unread_count(user_id=current_user.id)
    return UnreadCountSchema(count=count)


# =============================================================================
# Ações sobre notificações
# =============================================================================


@router.patch("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_as_read(
    current_user: CurrentUser,
    service: NotificationServiceDep,
):
    """Marca todas as notificações do usuário como lidas."""
    count = await service.mark_all_as_read(user_id=current_user.id)
    return {"updated": count}


@router.delete("/read", status_code=status.HTTP_200_OK)
async def delete_read_notifications(
    current_user: CurrentUser,
    service: NotificationServiceDep,
):
    """Exclui todas as notificações já lidas do usuário."""
    count = await service.delete_read_notifications(user_id=current_user.id)
    return {"deleted": count}



@router.patch("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_as_read(
    notification_id: UUID,
    current_user: CurrentUser,
    service: NotificationServiceDep,
):
    """Marca uma notificação como lida (executado ao clicar na notificação)."""
    success = await service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada ou já lida",
        )
    return {"ok": True}


# =============================================================================
# Gerenciamento de Push Tokens
# =============================================================================


@router.post("/push-token", status_code=status.HTTP_201_CREATED)
async def register_push_token(
    current_user: CurrentUser,
    service: NotificationServiceDep,
    token: str = Body(..., description="Expo Push Token do dispositivo"),
    device_id: str | None = Body(None, description="Identificador do dispositivo"),
    platform: str | None = Body(None, description="'ios' ou 'android'"),
):
    """
    Registra ou reativa o Expo Push Token do dispositivo.

    Deve ser chamado ao fazer login ou sempre que o token for renovado pelo Expo.
    """
    await service.register_push_token(
        user_id=current_user.id,
        token=token,
        device_id=device_id,
        platform=platform,
    )
    return {"ok": True}


@router.delete("/push-token/{token}", status_code=status.HTTP_200_OK)
async def unregister_push_token(
    token: str,
    current_user: CurrentUser,
    service: NotificationServiceDep,
):
    """
    Remove o push token (chamado no logout ou desinstalação do app).

    Só remove tokens pertencentes ao usuário autenticado.
    """
    success = await service.unregister_push_token(
        user_id=current_user.id,
        token=token,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token não encontrado",
        )
    return {"ok": True}
