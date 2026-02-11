import { useQuery } from '@tanstack/react-query';
import { getConversations } from '../api/chatApi';
import { useWebSocketStore } from '../../../../lib/websocketStore';

export function useConversations() {
    const isConnected = useWebSocketStore((s) => s.isConnected);

    return useQuery({
        queryKey: ['chat-conversations'],
        queryFn: getConversations,
        refetchInterval: isConnected ? false : 30000, // Fallback: polling 30s se WS desconectar
    });
}
