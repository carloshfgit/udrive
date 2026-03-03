/**
 * GoDrive Mobile - Notifications API
 *
 * Funções para consumir os endpoints de notificações.
 * Segue o padrão de chatApi.ts.
 */

import api, { SHARED_API } from '../../../../lib/axios';
import type {
    NotificationListResponse,
    UnreadCountResponse,
} from '../types/notification.types';

// === Funções de API ===

/**
 * Lista notificações do usuário autenticado (paginado).
 */
export async function getNotifications(
    limit: number = 50,
    offset: number = 0
): Promise<NotificationListResponse> {
    const response = await api.get<NotificationListResponse>(
        `${SHARED_API}/notifications/`,
        { params: { limit, offset } }
    );
    return response.data;
}

/**
 * Retorna contagem de notificações não lidas (para o badge do sininho).
 */
export async function getUnreadCount(): Promise<UnreadCountResponse> {
    const response = await api.get<UnreadCountResponse>(
        `${SHARED_API}/notifications/unread-count`
    );
    return response.data;
}

/**
 * Marca uma notificação como lida.
 */
export async function markAsRead(notificationId: string): Promise<void> {
    await api.patch(`${SHARED_API}/notifications/${notificationId}/read`);
}

/**
 * Marca todas as notificações como lidas.
 */
export async function markAllAsRead(): Promise<void> {
    await api.patch(`${SHARED_API}/notifications/read-all`);
}

/**
 * Exclui todas as notificações já lidas.
 */
export async function clearReadNotifications(): Promise<void> {
    await api.delete(`${SHARED_API}/notifications/read`);
}
