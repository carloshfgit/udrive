import { useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMessages, sendMessage, SendMessageRequest } from '../api/chatApi';
import { wsService } from '../../../../lib/websocket';
import { useWebSocketStore } from '../../../../lib/websocketStore';

export function useMessages(otherUserId: string) {
    const queryClient = useQueryClient();
    const isConnected = useWebSocketStore((s) => s.isConnected);

    // Query inicial para carregar histórico — polling apenas como fallback
    const query = useQuery({
        queryKey: ['chat-messages', otherUserId],
        queryFn: () => getMessages(otherUserId),
        enabled: !!otherUserId,
        refetchInterval: isConnected ? false : 5000, // Fallback: polling 5s se WS desconectar
    });

    // Fallback REST para envio quando WS está desconectado
    const sendMutationRest = useMutation({
        mutationFn: (content: string) => sendMessage({ receiver_id: otherUserId, content }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['chat-messages', otherUserId] });
            queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
        },
    });

    // Enviar mensagem via WebSocket (primário) ou REST (fallback)
    const handleSendMessage = useCallback(
        async (content: string) => {
            if (isConnected) {
                // Envio via WebSocket — resposta chega via evento `message_sent`
                wsService.send({
                    type: 'send_message',
                    receiver_id: otherUserId,
                    content,
                });
            } else {
                // Fallback REST quando WS está desconectado
                await sendMutationRest.mutateAsync(content);
            }
        },
        [isConnected, otherUserId, sendMutationRest]
    );

    // Marcar mensagens como lidas automaticamente quando o chat está aberto
    useEffect(() => {
        if (!isConnected || !query.data || query.data.length === 0) return;

        // Filtrar mensagens não lidas enviadas pelo outro usuário
        const unreadIds = query.data
            .filter((m) => !m.is_read && m.sender_id === otherUserId)
            .map((m) => m.id);

        if (unreadIds.length > 0) {
            wsService.send({
                type: 'mark_as_read',
                message_ids: unreadIds,
                sender_id: otherUserId, // Opcional, mas ajuda o servidor a saber quem notificar
            });

            // Otimismo: invalidar queries locais para limpar o estado de não lidas visualmente
            queryClient.invalidateQueries({ queryKey: ['chat-unread-count'] });
        }
    }, [query.data, isConnected, otherUserId, queryClient]);

    // Invalida a lista de conversas e contagem global quando as mensagens são carregadas com sucesso
    // Isso garante que os indicadores de não lidas sejam atualizados após abrir o chat
    useEffect(() => {
        if (query.isSuccess && query.data) {
            const timer = setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
                queryClient.invalidateQueries({ queryKey: ['chat-student-conversations'] });
                queryClient.invalidateQueries({ queryKey: ['chat-unread-count'] });
            }, 500);

            return () => clearTimeout(timer);
        }
    }, [query.isSuccess, query.dataUpdatedAt, queryClient]);

    return {
        ...query,
        messages: query.data || [],
        sendMessage: handleSendMessage,
        isSending: sendMutationRest.isPending,
    };
}
