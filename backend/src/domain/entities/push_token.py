"""
PushToken Entity

Entidade de domínio representando um token de push notification de um dispositivo.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class PushToken:
    """
    Entidade de push token do sistema GoDrive.

    Armazena o Expo Push Token de um dispositivo de um usuário,
    permitindo o envio de notificações push quando o app está em background.
    """

    user_id: UUID
    token: str
    id: UUID = field(default_factory=uuid4)
    device_id: str | None = None
    platform: str | None = None  # 'ios' | 'android'
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def deactivate(self) -> None:
        """Desativa o token (dispositivo inválido ou usuário deslogou)."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
