"""
IPushNotificationService Interface

Interface abstrata para serviço de envio de push notifications.
"""

from abc import ABC, abstractmethod
from uuid import UUID


class IPushNotificationService(ABC):
    """
    Interface abstrata para serviço de push notifications.

    Define como enviar notificações push para dispositivos de usuários
    e como gerenciar os tokens de dispositivo.
    """

    @abstractmethod
    async def send_to_user(
        self,
        user_id: UUID,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> None:
        """
        Envia push notification para todos os dispositivos ativos do usuário.

        Args:
            user_id: ID do usuário destinatário.
            title: Título da notificação.
            body: Corpo da notificação.
            data: Dados extras para navegação (deep link).
        """
        ...

    @abstractmethod
    async def register_token(
        self,
        user_id: UUID,
        token: str,
        device_id: str | None = None,
        platform: str | None = None,
    ) -> None:
        """
        Registra ou atualiza o push token de um dispositivo.

        Args:
            user_id: ID do usuário dono do dispositivo.
            token: Expo Push Token do dispositivo.
            device_id: Identificador único do dispositivo (opcional).
            platform: Plataforma do dispositivo ('ios' ou 'android').
        """
        ...

    @abstractmethod
    async def unregister_token(self, token: str, user_id: UUID) -> None:
        """
        Remove (desativa) o push token de um dispositivo.

        Chamado no logout ou quando o token é invalidado pelo provider.

        Args:
            token: Expo Push Token a remover.
            user_id: ID do usuário dono do token (validação de ownership).
        """
        ...
