/**
 * useInAppBanners Hook
 *
 * Escuta eventos NOTIFICATION do WebSocket e enfileira
 * banners in-app para exibição ao usuário.
 *
 * Mapeia os tipos de notificação do backend para os tipos
 * visuais do banner (scheduling, chat, reschedule, info).
 *
 * Deve ser chamado uma vez no RootNavigator.
 */

import { useEffect } from 'react';
import { wsService, WSMessage } from '../../lib/websocket';
import { useAuthStore } from '../../lib/store';
import { useInAppBannerStore, InAppBannerType } from '../stores/inAppBannerStore';
import type { ActionType } from '../../features/shared-features/notifications/types/notification.types';

/**
 * Mapeamento de NotificationType do backend → tipo visual do banner.
 * Apenas os tipos listados aqui geram banner in-app.
 */
const NOTIFICATION_TYPE_TO_BANNER: Record<string, InAppBannerType> = {
    NEW_SCHEDULING: 'scheduling',
    SCHEDULING_STATUS_CHANGED: 'scheduling',
    RESCHEDULE_REQUESTED: 'reschedule',
    RESCHEDULE_RESPONDED: 'reschedule',
    NEW_CHAT_MESSAGE: 'chat',
};

/**
 * Hook que conecta os eventos NOTIFICATION do WebSocket
 * ao sistema de banners in-app.
 */
export function useInAppBanners(): void {
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const enqueue = useInAppBannerStore((s) => s.enqueue);

    useEffect(() => {
        if (!isAuthenticated) return;

        const unsubscribe = wsService.onMessage((message: WSMessage) => {
            // Processar apenas eventos NOTIFICATION
            if (message.type !== 'NOTIFICATION') return;

            // NOTA: O backend envia NOTIFICATION com chave "payload" (não "data").
            // Chat events usam "data", mas NOTIFICATION usa "payload".
            // O tipo WSMessage declara "data?", mas em runtime o objeto tem "payload".
            const rawMessage = message as Record<string, any>;
            const payload = rawMessage.payload || rawMessage.data;
            if (!payload) return;

            // O payload.notification contém os dados da notificação persistida
            const notification = payload.notification as {
                type?: string;
                title?: string;
                body?: string;
                action_type?: ActionType | null;
                action_id?: string | null;
            } | undefined;

            if (!notification?.type || !notification?.title) return;

            // Verificar se este tipo de notificação deve gerar banner
            const bannerType = NOTIFICATION_TYPE_TO_BANNER[notification.type];
            if (!bannerType) return;

            enqueue({
                title: notification.title,
                body: notification.body || '',
                type: bannerType,
                actionType: notification.action_type ?? undefined,
                actionId: notification.action_id ?? undefined,
                notificationType: notification.type,
            });
        });

        return () => {
            unsubscribe();
        };
    }, [isAuthenticated, enqueue]);
}
