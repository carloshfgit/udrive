# Sistema de Notificações — GoDrive

Plano de construção por etapas para um sistema de notificações robusto, escalável e alinhado à Clean Architecture do projeto.

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Tipos de Notificação por Usuário](#2-tipos-de-notificação-por-usuário)
3. [Arquitetura do Sistema](#3-arquitetura-do-sistema)
4. [Etapa 1 — Modelagem de Dados](#etapa-1--modelagem-de-dados)
5. [Etapa 2 — Domain Layer](#etapa-2--domain-layer)
6. [Etapa 3 — Application Layer](#etapa-3--application-layer)
7. [Etapa 4 — Infrastructure Layer](#etapa-4--infrastructure-layer)
8. [Etapa 5 — Interface Layer (API + WebSocket)](#etapa-5--interface-layer-api--websocket)
9. [Etapa 6 — Push Notifications (Expo)](#etapa-6--push-notifications-expo)
10. [Etapa 7 — Celery Tasks (Lembretes e Avaliação)](#etapa-7--celery-tasks-lembretes-e-avaliação)
11. [Etapa 8 — Mobile: Feature de Notificações](#etapa-8--mobile-feature-de-notificações)
12. [Etapa 9 — Integração nos Fluxos Existentes](#etapa-9--integração-nos-fluxos-existentes)
13. [Etapa 10 — Testes e Verificação](#etapa-10--testes-e-verificação)
14. [Decisões de Design e Boas Práticas](#decisões-de-design-e-boas-práticas)

---

## 1. Visão Geral

O sistema de notificações opera em três canais complementares:

```
┌─────────────────────────────────────────────────────────┐
│                   EVENTO DE NEGÓCIO                     │
│  (novo agendamento, mensagem, pagamento, etc.)          │
└──────────────────┬──────────────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  NotificationService│   (Application Layer)
         │  (Orquestra tudo)   │
         └──┬───────┬───────┬──┘
            │       │       │
     ┌──────▼──┐ ┌──▼───┐ ┌▼────────────┐
     │ Persist │ │ WS   │ │ Push (Expo)  │
     │ (DB)    │ │ Real │ │ Background   │
     │         │ │ Time │ │              │
     └─────────┘ └──────┘ └──────────────┘
```

| Canal | Quando | Benefício |
|-------|--------|-----------|
| **Persistência (DB)** | Sempre | Histórico no sininho, nunca perde notificação |
| **WebSocket (real-time)** | Usuário online no app | Feedback instantâneo, badge do sininho atualiza |
| **Push Notification (Expo)** | Usuário offline / app em background | Garante recebimento mesmo sem o app aberto |

---

## 2. Tipos de Notificação por Usuário

### Instrutor

| Tipo | Evento Gatilho | Deep Link (destino no app) |
|------|----------------|----------------------------|
| `NEW_SCHEDULING` | Aluno cria agendamento | Tela de detalhes do agendamento |
| `RESCHEDULE_REQUESTED` | Aluno solicita reagendamento | Tela de detalhes do reagendamento |
| `RESCHEDULE_RESPONDED` | Aluno responde reagendamento | Tela de detalhes do agendamento |
| `NEW_CHAT_MESSAGE` | Aluno envia mensagem | Tela do chat com o aluno |
| `LESSON_REMINDER` | 30min antes da aula | Tela de detalhes do agendamento |

### Aluno

| Tipo | Evento Gatilho | Deep Link (destino no app) |
|------|----------------|----------------------------|
| `PAYMENT_STATUS_CHANGED` | Status do pagamento altera | Tela de detalhes do agendamento |
| `SCHEDULING_STATUS_CHANGED` | Instrutor confirma/cancela aula | Tela de detalhes do agendamento |
| `RESCHEDULE_REQUESTED` | Instrutor solicita reagendamento | Tela de detalhes do reagendamento |
| `RESCHEDULE_RESPONDED` | Instrutor responde reagendamento | Tela de detalhes do agendamento |
| `NEW_CHAT_MESSAGE` | Instrutor envia mensagem | Tela do chat com o instrutor |
| `LESSON_REMINDER` | 30min antes da aula | Tela de detalhes do agendamento |
| `REVIEW_REQUEST` | 1h após término da aula | Tela de avaliação do instrutor |

---

## 3. Arquitetura do Sistema

Seguindo a Clean Architecture do projeto:

```
domain/
├── entities/
│   └── notification.py            # Entidade Notification (dataclass)
└── interfaces/
    └── notification_repository.py # INotificationRepository (Protocol)

application/
├── dtos/
│   └── notification_dtos.py       # NotificationDTO, CreateNotificationDTO
├── use_cases/
│   └── common/
│       ├── create_notification.py # CreateNotificationUseCase
│       ├── get_notifications.py   # GetNotificationsUseCase
│       └── mark_notification.py   # MarkAsReadUseCase
└── services/
    └── notification_service.py    # NotificationService (orquestra persist + dispatch)

infrastructure/
├── db/
│   └── models/
│       └── notification_model.py  # SQLAlchemy Model
├── repositories/
│   └── notification_repository.py # Implementação concreta
├── services/
│   └── push_notification_service.py # ExponentPushService
└── tasks/
    └── notification_tasks.py      # Celery: lembretes e avaliação

interface/
└── api/
    └── v1/
        └── shared/
            └── notifications.py   # Endpoints REST
```

---

## Etapa 1 — Modelagem de Dados

### Tabela `notifications`

```sql
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Tipo e conteúdo
    type            VARCHAR(50) NOT NULL,      -- Enum (NEW_SCHEDULING, LESSON_REMINDER, etc.)
    title           VARCHAR(255) NOT NULL,     -- "Nova aula agendada!"
    body            TEXT NOT NULL,             -- "João agendou uma aula para 15/03 às 14h"
    
    -- Navegação (deep link)
    action_type     VARCHAR(50),               -- Tipo de tela destino (SCHEDULING, CHAT, REVIEW)
    action_id       UUID,                      -- ID do recurso (scheduling_id, user_id para chat, etc.)
    
    -- Estado
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Audit
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    read_at         TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX ix_notifications_user_unread 
    ON notifications (user_id, is_read, created_at DESC)
    WHERE is_read = FALSE;

CREATE INDEX ix_notifications_user_created 
    ON notifications (user_id, created_at DESC);
```

**Decisões importantes:**
- **Índice parcial `WHERE is_read = FALSE`**: Otimiza a query mais frequente (contagem de não-lidas para o badge).
- **Campos `action_type` + `action_id`**: Permitem deep linking genérico sem acoplar ao tipo de notificação.
- **Sem soft delete**: Notificações antigas podem ser deletadas via cron/task após 90 dias.

### Tabela `push_tokens`

```sql
CREATE TABLE push_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL,   -- Expo Push Token
    device_id   VARCHAR(255),            -- Identificador do dispositivo
    platform    VARCHAR(10),             -- 'ios' | 'android'
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT uq_push_tokens_token UNIQUE (token)
);

CREATE INDEX ix_push_tokens_user_active 
    ON push_tokens (user_id) 
    WHERE is_active = TRUE;
```

### Migration

```bash
docker compose exec backend alembic revision -m "criar_tabelas_notifications_e_push_tokens"
```

---

## Etapa 2 — Domain Layer

### Entidade `Notification`

```python
# backend/src/domain/entities/notification.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class NotificationType(str, Enum):
    """Tipos de notificação suportados pelo sistema."""
    NEW_SCHEDULING = "NEW_SCHEDULING"
    RESCHEDULE_REQUESTED = "RESCHEDULE_REQUESTED"
    RESCHEDULE_RESPONDED = "RESCHEDULE_RESPONDED"
    NEW_CHAT_MESSAGE = "NEW_CHAT_MESSAGE"
    LESSON_REMINDER = "LESSON_REMINDER"
    PAYMENT_STATUS_CHANGED = "PAYMENT_STATUS_CHANGED"
    SCHEDULING_STATUS_CHANGED = "SCHEDULING_STATUS_CHANGED"
    REVIEW_REQUEST = "REVIEW_REQUEST"


class ActionType(str, Enum):
    """Tipos de ação (destino do deep link)."""
    SCHEDULING = "SCHEDULING"
    CHAT = "CHAT"
    REVIEW = "REVIEW"
    PAYMENT = "PAYMENT"


@dataclass
class Notification:
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    action_type: ActionType | None = None
    action_id: UUID | None = None
    is_read: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: datetime | None = None
```

### Interface `INotificationRepository`

```python
# backend/src/domain/interfaces/notification_repository.py
from typing import Protocol
from uuid import UUID
from src.domain.entities.notification import Notification


class INotificationRepository(Protocol):
    """Abstração do repositório de notificações."""

    async def create(self, notification: Notification) -> Notification:
        """Persiste uma nova notificação."""
        ...

    async def get_by_user(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Notification]:
        """Retorna notificações do usuário (mais recentes primeiro)."""
        ...

    async def count_unread(self, user_id: UUID) -> int:
        """Conta notificações não lidas."""
        ...

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        """Marca uma notificação como lida. Retorna True se bem-sucedido."""
        ...

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Marca todas como lidas. Retorna a quantidade atualizada."""
        ...
```

---

## Etapa 3 — Application Layer

### DTOs

```python
# backend/src/application/dtos/notification_dtos.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class NotificationResponseDTO(BaseModel):
    id: UUID
    type: str
    title: str
    body: str
    action_type: str | None
    action_id: UUID | None
    is_read: bool
    created_at: datetime
    read_at: datetime | None

    class Config:
        from_attributes = True


class NotificationListDTO(BaseModel):
    notifications: list[NotificationResponseDTO]
    unread_count: int
    total: int


class UnreadCountDTO(BaseModel):
    count: int
```

### `NotificationService` — Orquestrador Central

```python
# backend/src/application/services/notification_service.py

class NotificationService:
    """
    Orquestra a criação de notificações em 3 canais:
    1. Persistência no banco (sempre)
    2. Envio real-time via WebSocket (se online)
    3. Push notification via Expo (se offline ou em background)
    """

    def __init__(
        self,
        repository: INotificationRepository,
        push_service: IPushNotificationService,
        ws_manager: ConnectionManager,
    ):
        self._repository = repository
        self._push_service = push_service
        self._ws_manager = ws_manager

    async def notify(
        self,
        user_id: UUID,
        notification_type: NotificationType,
        title: str,
        body: str,
        action_type: ActionType | None = None,
        action_id: UUID | None = None,
    ) -> Notification:
        """
        Pipeline completo de notificação:
        1. Persiste no DB
        2. Envia via WebSocket (se online)
        3. Envia Push (se offline)
        """
        # 1. Persistir
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            action_type=action_type,
            action_id=action_id,
        )
        saved = await self._repository.create(notification)

        # 2. Real-time via WebSocket
        if self._ws_manager.is_online(user_id):
            unread = await self._repository.count_unread(user_id)
            await self._ws_manager.send_to_user(user_id, {
                "type": "NOTIFICATION",
                "payload": {
                    "notification": NotificationResponseDTO.from_orm(saved).dict(),
                    "unread_count": unread,
                },
            })
        else:
            # 3. Push notification (apenas se offline)
            await self._push_service.send_to_user(
                user_id=user_id,
                title=title,
                body=body,
                data={
                    "type": notification_type.value,
                    "action_type": action_type.value if action_type else None,
                    "action_id": str(action_id) if action_id else None,
                },
            )

        return saved
```

**Decisão de design — Push apenas quando offline:**
Evita notificações duplicadas (in-app + push ao mesmo tempo). Se o usuário está no app, ele vê o badge e o WebSocket atualiza em tempo real.

---

## Etapa 4 — Infrastructure Layer

### SQLAlchemy Model

```python
# backend/src/infrastructure/db/models/notification_model.py

class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    action_type = Column(String(50), nullable=True)
    action_id = Column(UUID(as_uuid=True), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relacionamento
    user = relationship("UserModel", back_populates="notifications")
```

### Push Tokens Model

```python
# backend/src/infrastructure/db/models/push_token_model.py

class PushTokenModel(Base):
    __tablename__ = "push_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    device_id = Column(String(255), nullable=True)
    platform = Column(String(10), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
```

### Repositório Concreto

```python
# backend/src/infrastructure/repositories/notification_repository.py

class NotificationRepository:
    """Implementação concreta do INotificationRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, notification: Notification) -> Notification:
        model = NotificationModel(**asdict(notification))
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_user(self, user_id: UUID, limit: int = 50, offset: int = 0) -> list[Notification]:
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_unread(self, user_id: UUID) -> int:
        stmt = (
            select(func.count())
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.is_read == False)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .where(NotificationModel.user_id == user_id)
            .values(is_read=True, read_at=func.now())
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: UUID) -> int:
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.is_read == False)
            .values(is_read=True, read_at=func.now())
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount
```

### Expo Push Notification Service

```python
# backend/src/infrastructure/services/push_notification_service.py

import httpx
import structlog

logger = structlog.get_logger()

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


class ExpoPushService:
    """Serviço de envio de push notifications via Expo."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def send_to_user(
        self, user_id: UUID, title: str, body: str, data: dict | None = None
    ) -> None:
        """Envia push para todos os dispositivos ativos do usuário."""
        tokens = await self._get_active_tokens(user_id)
        if not tokens:
            logger.info("push_no_tokens", user_id=str(user_id))
            return

        messages = [
            {
                "to": token,
                "title": title,
                "body": body,
                "data": data or {},
                "sound": "default",
                "priority": "high",
                "channelId": "default",
            }
            for token in tokens
        ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                EXPO_PUSH_URL,
                json=messages,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code != 200:
                logger.error("push_send_failed", status=response.status_code)
            else:
                # Processar respostas para desativar tokens inválidos
                await self._handle_receipts(response.json(), tokens)

    async def _get_active_tokens(self, user_id: UUID) -> list[str]:
        stmt = (
            select(PushTokenModel.token)
            .where(PushTokenModel.user_id == user_id)
            .where(PushTokenModel.is_active == True)
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def _handle_receipts(self, response_data: dict, tokens: list[str]) -> None:
        """Desativa tokens inválidos (DeviceNotRegistered, etc.)."""
        for i, ticket in enumerate(response_data.get("data", [])):
            if ticket.get("status") == "error":
                error_type = ticket.get("details", {}).get("error")
                if error_type == "DeviceNotRegistered":
                    await self._deactivate_token(tokens[i])

    async def _deactivate_token(self, token: str) -> None:
        stmt = (
            update(PushTokenModel)
            .where(PushTokenModel.token == token)
            .values(is_active=False)
        )
        await self._session.execute(stmt)
        await self._session.commit()
        logger.info("push_token_deactivated", token=token[:20] + "...")
```

---

## Etapa 5 — Interface Layer (API + WebSocket)

### Endpoints REST

```python
# backend/src/interface/api/v1/shared/notifications.py

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=NotificationListDTO)
async def list_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Lista notificações do usuário autenticado (paginado)."""
    ...


@router.get("/unread-count", response_model=UnreadCountDTO)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Retorna contagem de notificações não lidas (para o badge do sininho)."""
    ...


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Marca uma notificação como lida (quando o usuário clica nela)."""
    ...


@router.patch("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Marca todas as notificações como lidas."""
    ...


@router.post("/push-token")
async def register_push_token(
    token: str = Body(...),
    device_id: str | None = Body(None),
    platform: str | None = Body(None),
    current_user: User = Depends(get_current_user),
):
    """Registra ou atualiza o Expo Push Token do dispositivo."""
    ...


@router.delete("/push-token/{token}")
async def unregister_push_token(
    token: str,
    current_user: User = Depends(get_current_user),
):
    """Remove push token (logout ou desinstalação)."""
    ...
```

### Evento WebSocket

A estrutura WebSocket existente (`connection_manager.py`, `event_dispatcher.py`) já suporta envio por `user_id`. Basta definir um novo tipo de mensagem:

```python
# Adição em message_types.py
class NotificationEventType(str, Enum):
    NOTIFICATION = "NOTIFICATION"           # Nova notificação
    UNREAD_COUNT_UPDATE = "UNREAD_COUNT"    # Atualização do badge
```

O `NotificationService` já usa `ws_manager.send_to_user()` para real-time — nenhuma alteração é necessária no `ConnectionManager` existente.

---

## Etapa 6 — Push Notifications (Expo)

### Configuração no Mobile

```bash
# Instalar dependências
npx expo install expo-notifications expo-device expo-constants
```

### Hook de Registro

```typescript
// mobile/src/shared/hooks/usePushNotifications.ts

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { useEffect, useRef } from 'react';
import { Platform } from 'react-native';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { api } from '@/lib/api';

// Configuração do handler de notificações
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export function usePushNotifications() {
  const { user } = useAuth();
  const notificationListener = useRef<Notifications.Subscription>();
  const responseListener = useRef<Notifications.Subscription>();

  useEffect(() => {
    if (!user) return;

    registerForPushNotifications();

    // Listener: notificação recebida com app aberto
    notificationListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        // Atualizar contagem de não-lidas via Zustand
      }
    );

    // Listener: usuário clicou na notificação
    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        const data = response.notification.request.content.data;
        handleNotificationPress(data);
      }
    );

    return () => {
      notificationListener.current?.remove();
      responseListener.current?.remove();
    };
  }, [user]);

  async function registerForPushNotifications() {
    if (!Device.isDevice) return;

    const { status } = await Notifications.requestPermissionsAsync();
    if (status !== 'granted') return;

    const tokenData = await Notifications.getExpoPushTokenAsync();
    
    // Registrar no backend
    await api.post('/notifications/push-token', {
      token: tokenData.data,
      platform: Platform.OS,
    });
  }
}
```

### Navegação ao clicar na notificação

```typescript
// mobile/src/shared/hooks/useNotificationNavigation.ts

import { useNavigation } from '@react-navigation/native';

interface NotificationData {
  type: string;
  action_type: 'SCHEDULING' | 'CHAT' | 'REVIEW' | 'PAYMENT';
  action_id: string;
}

export function useNotificationNavigation() {
  const navigation = useNavigation();

  function handleNotificationPress(data: NotificationData) {
    switch (data.action_type) {
      case 'SCHEDULING':
        navigation.navigate('ScheduleDetails', { schedulingId: data.action_id });
        break;
      case 'CHAT':
        navigation.navigate('ChatScreen', { otherUserId: data.action_id });
        break;
      case 'REVIEW':
        navigation.navigate('ReviewScreen', { schedulingId: data.action_id });
        break;
      case 'PAYMENT':
        navigation.navigate('ScheduleDetails', { schedulingId: data.action_id });
        break;
    }
  }

  return { handleNotificationPress };
}
```

---

## Etapa 7 — Celery Tasks (Lembretes e Avaliação)

As notificações de lembrete (30min antes) e solicitação de avaliação (1h após) requerem **tarefas agendadas (scheduled tasks)**. Usamos Celery + Redis conforme `PROJECT_GUIDELINES.md`.

### Tasks

```python
# backend/src/infrastructure/tasks/notification_tasks.py

from celery import shared_task
from datetime import timedelta

@shared_task(name="send_lesson_reminder")
def send_lesson_reminder(scheduling_id: str) -> None:
    """
    Envia lembrete de aula para ambos os participantes.
    Agendada para disparar 30min antes da aula.
    """
    # 1. Buscar agendamento
    # 2. Verificar se status ainda é CONFIRMED
    # 3. Notificar instrutor e aluno via NotificationService
    ...


@shared_task(name="send_review_request")
def send_review_request(scheduling_id: str) -> None:
    """
    Notifica o aluno para avaliar o instrutor.
    Agendada para 1h após o término da aula.
    """
    # 1. Buscar agendamento
    # 2. Verificar se status é COMPLETED e se já não existe review
    # 3. Notificar aluno via NotificationService
    ...
```

### Agendamento das Tasks

As Celery tasks são agendadas **no momento em que o agendamento é confirmado**:

```python
# Dentro do use case de confirmação de agendamento:

from src.infrastructure.tasks.notification_tasks import (
    send_lesson_reminder,
    send_review_request,
)

# Lembrete: 30min antes da aula
reminder_eta = scheduling.scheduled_datetime - timedelta(minutes=30)
send_lesson_reminder.apply_async(
    args=[str(scheduling.id)],
    eta=reminder_eta,
    task_id=f"reminder-{scheduling.id}",  # ID determinístico para revogação
)

# Avaliação: 1h após o término
lesson_end = scheduling.scheduled_datetime + timedelta(minutes=scheduling.duration_minutes)
review_eta = lesson_end + timedelta(hours=1)
send_review_request.apply_async(
    args=[str(scheduling.id)],
    eta=review_eta,
    task_id=f"review-{scheduling.id}",
)
```

**Importante — Cancelamento/Reagendamento:**
Ao cancelar ou reagendar uma aula, **revogar as tasks pendentes** e reagendar se necessário:

```python
from celery.result import AsyncResult

# Revogar tasks antigas
app.control.revoke(f"reminder-{scheduling.id}", terminate=True)
app.control.revoke(f"review-{scheduling.id}", terminate=True)
```

---

## Etapa 8 — Mobile: Feature de Notificações

### Estrutura de Arquivos

```
mobile/src/features/shared-features/notifications/
├── api/
│   └── notificationsApi.ts        # Funções de fetch (React Query)
├── components/
│   ├── NotificationBell.tsx       # Ícone de sininho com badge
│   ├── NotificationItem.tsx       # Card individual de notificação
│   └── NotificationList.tsx       # Lista de notificações
├── hooks/
│   ├── useNotifications.ts        # React Query hooks
│   └── useUnreadCount.ts          # Hook para badge count
├── screens/
│   └── NotificationsScreen.tsx    # Tela de histórico de notificações
├── stores/
│   └── notificationStore.ts       # Zustand store para badge real-time
└── types/
    └── notification.types.ts      # Tipos TypeScript
```

### Componente `NotificationBell`

```typescript
// mobile/src/features/shared-features/notifications/components/NotificationBell.tsx

import { TouchableOpacity, View, Text } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useUnreadCount } from '../hooks/useUnreadCount';

interface NotificationBellProps {
  onPress: () => void;
}

export function NotificationBell({ onPress }: NotificationBellProps) {
  const { count } = useUnreadCount();

  return (
    <TouchableOpacity onPress={onPress}>
      <Ionicons name="notifications-outline" size={24} color="#333" />
      {count > 0 && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>
            {count > 99 ? '99+' : count}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}
```

### Tela `NotificationsScreen`

- **FlatList** com pull-to-refresh e paginação infinita
- Cada item mostra ícone do tipo, título, body e timestamp relativo ("há 5 min")
- Ao clicar, navega para o deep link e marca como lida
- Header com botão "Marcar todas como lidas"
- Notificações não lidas têm fundo levemente colorido para destaque visual

### Integração nas Home Screens

O `NotificationBell` deve ser adicionado no header das home screens:

```
InstructorHomeScreen.tsx  → Header com NotificationBell (direita)
StudentHomeScreen.tsx     → Header com NotificationBell (direita)
```

### Estado Real-Time (Zustand + WebSocket)

```typescript
// mobile/src/features/shared-features/notifications/stores/notificationStore.ts

import { create } from 'zustand';

interface NotificationStore {
  unreadCount: number;
  setUnreadCount: (count: number) => void;
  incrementUnread: () => void;
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  unreadCount: 0,
  setUnreadCount: (count) => set({ unreadCount: count }),
  incrementUnread: () => set((state) => ({ unreadCount: state.unreadCount + 1 })),
}));
```

O listener WebSocket existente deve ser estendido para capturar mensagens do tipo `NOTIFICATION` e atualizar o Zustand store.

---

## Etapa 9 — Integração nos Fluxos Existentes

Os eventos de negócio que disparam notificações devem chamar o `NotificationService.notify()` na camada `application` ou na camada de dispatch (como já feito no `SchedulingEventDispatcher`).

### Mapeamento Evento → Notificação

| Momento/Fluxo | Quem chamar | Notificar quem? | Tipo |
|---|---|---|---|
| Aluno cria agendamento | `book_lesson` use case | Instrutor | `NEW_SCHEDULING` |
| Instrutor confirma aula | `accept_booking` use case | Aluno | `SCHEDULING_STATUS_CHANGED` |
| Qualquer parte cancela | `cancel_booking` use case | Outra parte | `SCHEDULING_STATUS_CHANGED` |
| Solicitação de reagendamento | `request_reschedule` use case | Outra parte | `RESCHEDULE_REQUESTED` |
| Resposta de reagendamento | `respond_reschedule` use case | Solicitante | `RESCHEDULE_RESPONDED` |
| Nova mensagem no chat | `chat_handler.py` (WebSocket) | Destinatário | `NEW_CHAT_MESSAGE` |
| Status de pagamento muda | Webhook Mercado Pago | Aluno | `PAYMENT_STATUS_CHANGED` |
| 30min antes da aula | Celery task agendada | Ambos | `LESSON_REMINDER` |
| 1h após término da aula | Celery task agendada | Aluno | `REVIEW_REQUEST` |

### Estratégia de Integração

Em vez de alterar diretamente os use cases existentes, considere **dois padrões**:

**Opção A — Decorator/Middleware Pattern (Recomendada)**
Criar um decorator que envolve os use cases e dispara notificações após a execução bem-sucedida. Mantém os use cases puros e desacoplados.

**Opção B — Injeção direta**
Injetar o `NotificationService` nos use cases que precisam notificar. Mais simples, mas acopla levemente os use cases ao serviço de notificação.

> **Recomendação**: Começar com **Opção B** (injeção direta) pela simplicidade. Migrar para Opção A quando a complexidade crescer. O `SchedulingEventDispatcher` já usa um padrão similar de "chamar após o fluxo principal".

---

## Etapa 10 — Testes e Verificação

### Testes Unitários (Backend)

```bash
docker compose exec backend pytest tests/unit/notifications/ -v
```

- `test_notification_service.py` — Mock do repository, WS manager e push service
- `test_notification_repository.py` — Testes com DB de teste (create, list, mark_as_read)
- `test_push_service.py` — Mock das chamadas HTTP à Expo API

### Testes de Integração (Backend)

```bash
docker compose exec backend pytest tests/integration/notifications/ -v
```

- Testar o fluxo completo: criar agendamento → notificação persiste → WebSocket envia
- Testar push token registration e unregistration

### Testes Mobile

- Verificar que o `NotificationBell` exibe badge correto
- Verificar que ao clicar em uma notificação, navega para a tela correta
- Verificar que notificações são marcadas como lidas ao clicar
- Testar o `usePushNotifications` em device físico (push não funciona no emulador)

### Verificação Manual

1. Criar agendamento → instrutor recebe notificação
2. Instrutor confirma → aluno recebe notificação
3. Enviar mensagem no chat → destinatário recebe notificação
4. Aguardar 30min antes de uma aula → ambos recebem lembrete
5. Completar aula → 1h depois, aluno recebe pedido de avaliação
6. Testar sininho: visualizar histórico, marcar como lida, marcar todas como lidas
7. Testar deep link: clicar na notificação redireciona corretamente
8. Testar push: fechar o app, gerar evento, push notification chega

---

## Decisões de Design e Boas Práticas

### ✅ Persistência Sempre
Toda notificação é persistida antes de ser enviada por qualquer canal. Isso garante que:
- O histórico no sininho é completo
- Falhas de WebSocket ou Push não perdem notificações

### ✅ Push Apenas Quando Offline
Se o usuário está online (WebSocket ativo), a notificação aparece in-app. Push é reservado para quando o usuário não está no aplicativo, evitando duplicidade.

### ✅ Deep Links Genéricos
Os campos `action_type` + `action_id` desacoplam a notificação da tela de destino. O mobile resolve o mapeamento localmente, permitindo evoluir a navegação sem alterar o backend.

### ✅ Tasks com ID Determinístico
As Celery tasks de lembrete e avaliação usam IDs previsíveis (`reminder-{scheduling_id}`), permitindo revogação fácil em caso de cancelamento ou reagendamento.

### ✅ Índice Parcial para Performance
O índice `WHERE is_read = FALSE` otimiza a contagem de não-lidas (operação mais frequente do badge) sem impactar o tamanho total do índice.

### ✅ Expo Push com Auto-Limpeza
Tokens inválidos (`DeviceNotRegistered`) são desativados automaticamente, mantendo a tabela `push_tokens` limpa e evitando envios desnecessários.

### ✅ Respeito à Clean Architecture
- **Domain**: Entidade e interface puras (sem dependência de framework)
- **Application**: Service e DTOs (regras de negócio)
- **Infrastructure**: Implementação concreta (SQLAlchemy, Expo HTTP)
- **Interface**: Endpoints REST e WebSocket

### ⚠️ Considerações Futuras
- **Preferências de notificação**: Permitir usuários desativar tipos específicos
- **Rate limiting de push**: Evitar flood de notificações no chat (agrupar mensagens)
- **Retenção**: Task periódica para limpar notificações lidas com mais de 90 dias
- **Analytics**: Métricas de taxa de abertura e clique em notificações
