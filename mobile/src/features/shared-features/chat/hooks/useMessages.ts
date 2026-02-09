import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMessages, sendMessage, SendMessageRequest } from '../api/chatApi';

export function useMessages(otherUserId: string) {
    const queryClient = useQueryClient();

    const query = useQuery({
        queryKey: ['chat-messages', otherUserId],
        queryFn: () => getMessages(otherUserId),
        refetchInterval: 5000, // Chat precisa de atualização mais frequente
        enabled: !!otherUserId,
    });

    const sendMutation = useMutation({
        mutationFn: (content: string) => sendMessage({ receiver_id: otherUserId, content }),
        onSuccess: () => {
            // Invalida para carregar a nova mensagem imediatamente
            queryClient.invalidateQueries({ queryKey: ['chat-messages', otherUserId] });
            queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
        },
    });

    return {
        ...query,
        messages: query.data || [],
        sendMessage: sendMutation.mutateAsync,
        isSending: sendMutation.isPending,
    };
}
