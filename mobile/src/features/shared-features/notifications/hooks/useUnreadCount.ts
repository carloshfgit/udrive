/**
 * useUnreadCount Hook
 *
 * Combina o valor do backend (React Query) com atualizações
 * real-time do Zustand store (via WebSocket).
 *
 * Padrão: polling 30s quando WebSocket desconectado.
 */

import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getUnreadCount } from '../api/notificationsApi';
import { useNotificationStore } from '../stores/notificationStore';
import { useWebSocketStore } from '../../../../lib/websocketStore';

export function useUnreadCount() {
    const isConnected = useWebSocketStore((s) => s.isConnected);
    const { unreadCount, setUnreadCount } = useNotificationStore();

    const query = useQuery({
        queryKey: ['notifications-unread-count'],
        queryFn: getUnreadCount,
        refetchInterval: isConnected ? false : 30000, // Fallback: polling 30s
    });

    // Sincronizar Zustand com o valor do backend quando chega
    useEffect(() => {
        if (query.data?.count !== undefined) {
            setUnreadCount(query.data.count);
        }
    }, [query.data?.count, setUnreadCount]);

    return {
        ...query,
        unreadCount,
    };
}
