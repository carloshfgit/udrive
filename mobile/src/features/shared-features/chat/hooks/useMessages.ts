import { useEffect } from 'react';
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

    // Invalida a lista de conversas quando as mensagens são carregadas com sucesso
    // Isso garante que os indicadores de não lidas sejam atualizados após abrir o chat
    useEffect(() => {
        if (query.isSuccess && query.data) {
            // Pequeno delay para garantir que o backend processou a marcação como lida
            const timer = setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
                queryClient.invalidateQueries({ queryKey: ['chat-student-conversations'] });
            }, 500);

            return () => clearTimeout(timer);
        }
    }, [query.isSuccess, query.dataUpdatedAt, queryClient]);

    return {
        ...query,
        messages: query.data || [],
        sendMessage: sendMutation.mutateAsync,
        isSending: sendMutation.isPending,
    };
}
