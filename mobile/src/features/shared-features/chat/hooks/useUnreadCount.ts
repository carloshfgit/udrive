import { useQuery } from '@tanstack/react-query';
import { getUnreadCount } from '../api/chatApi';
import { useWebSocketStore } from '../../../../lib/websocketStore';

export function useUnreadCount() {
    const isConnected = useWebSocketStore((s) => s.isConnected);

    const query = useQuery({
        queryKey: ['chat-unread-count'],
        queryFn: getUnreadCount,
        refetchInterval: isConnected ? false : 30000, // Fallback: polling 30s se WS desconectar
    });

    return {
        ...query,
        unreadCount: query.data?.unread_count ?? 0,
    };
}
