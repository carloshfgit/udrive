import { useQuery } from '@tanstack/react-query';
import { getStudentConversations } from '../api/chatApi';
import { useWebSocketStore } from '../../../../lib/websocketStore';

export function useStudentConversations() {
    const isConnected = useWebSocketStore((s) => s.isConnected);

    return useQuery({
        queryKey: ['chat-student-conversations'],
        queryFn: getStudentConversations,
        refetchInterval: isConnected ? false : 30000, // Fallback: polling 30s se WS desconectar
    });
}
