import { useQuery } from '@tanstack/react-query';
import { getConversations } from '../api/chatApi';

export function useConversations() {
    return useQuery({
        queryKey: ['chat-conversations'],
        queryFn: getConversations,
        refetchInterval: 30000, // Atualizar a cada 30 segundos
    });
}
