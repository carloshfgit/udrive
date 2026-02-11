/**
 * useWebSocket Hook
 *
 * Hook React que gerencia o ciclo de vida do WebSocket:
 * - Conecta automaticamente quando o usuário está autenticado
 * - Desconecta no logout
 * - Integra mensagens recebidas com React Query (cache update/invalidation)
 * - Expõe `send()` e `onEvent()` para componentes filhos
 *
 * Deve ser usado em um componente de alto nível (ex: App.tsx ou TabNavigator)
 * para garantir que o WebSocket fique ativo durante toda a sessão.
 */

import { useEffect, useCallback, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';

import { tokenManager } from '../../lib/axios';
import { wsService, WSMessage, MessageCallback } from '../../lib/websocket';
import { useWebSocketStore } from '../../lib/websocketStore';
import { useAuthStore } from '../../lib/store';

// Tipos de evento do servidor
const CHAT_EVENTS = [
    'new_message',
    'message_sent',
    'messages_read',
    'typing_indicator',
    'unread_count',
] as const;

const SCHEDULING_EVENTS = [
    'scheduling_created',
    'scheduling_confirmed',
    'scheduling_cancelled',
    'scheduling_started',
    'scheduling_completed',
    'reschedule_requested',
    'reschedule_responded',
] as const;

/**
 * Hook principal de WebSocket.
 *
 * Conecta/desconecta automaticamente com base na autenticação.
 * Processa mensagens e atualiza o cache do React Query.
 */
export function useWebSocket() {
    const queryClient = useQueryClient();
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
    const setStatus = useWebSocketStore((s) => s.setStatus);
    const isConnected = useWebSocketStore((s) => s.isConnected);

    // Ref para listeners de eventos customizados (ex: notificações de scheduling)
    const eventListenersRef = useRef<Set<MessageCallback>>(new Set());

    // =========================================================================
    // React Query Integration — Processar mensagens recebidas
    // =========================================================================

    const handleMessage = useCallback(
        (message: WSMessage) => {
            switch (message.type) {
                // --- Chat Events ---

                case 'new_message': {
                    // Nova mensagem recebida de outro usuário
                    const senderId = (message.data as Record<string, string>)?.sender_id;
                    if (senderId) {
                        // Atualizar cache de mensagens adicionando a nova mensagem
                        queryClient.setQueryData<unknown[]>(
                            ['chat-messages', senderId],
                            (old) => {
                                if (!old) return [message.data];
                                return [...old, message.data];
                            }
                        );
                        // Invalidar lista de conversas e contagem global para atualização em tempo real
                        queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
                        queryClient.invalidateQueries({ queryKey: ['chat-student-conversations'] });
                        queryClient.invalidateQueries({ queryKey: ['chat-unread-count'] });
                    }
                    break;
                }

                case 'message_sent': {
                    // Confirmação de que nossa mensagem foi salva
                    const receiverId = (message.data as Record<string, string>)?.receiver_id;
                    if (receiverId) {
                        queryClient.setQueryData<unknown[]>(
                            ['chat-messages', receiverId],
                            (old) => {
                                if (!old) return [message.data];
                                return [...old, message.data];
                            }
                        );
                        queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
                        queryClient.invalidateQueries({ queryKey: ['chat-student-conversations'] });
                    }
                    break;
                }

                case 'messages_read': {
                    // Nossas mensagens foram lidas pelo outro usuário
                    queryClient.invalidateQueries({ queryKey: ['chat-messages'] });
                    queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
                    queryClient.invalidateQueries({ queryKey: ['chat-student-conversations'] });
                    queryClient.invalidateQueries({ queryKey: ['chat-unread-count'] });
                    break;
                }

                case 'unread_count': {
                    // Contagem atualizada de mensagens não lidas (enviada explicitamente pelo servidor)
                    const count = (message.data as Record<string, number>)?.count;
                    if (count !== undefined) {
                        queryClient.setQueryData(['chat-unread-count'], { unread_count: count });
                        // Invalidar listas para atualizar os badges nos itens da lista
                        queryClient.invalidateQueries({ queryKey: ['chat-conversations'] });
                        queryClient.invalidateQueries({ queryKey: ['chat-student-conversations'] });
                    }
                    break;
                }

                // --- Scheduling Events ---

                case 'scheduling_created':
                case 'scheduling_confirmed':
                case 'scheduling_cancelled':
                case 'scheduling_started':
                case 'scheduling_completed':
                case 'reschedule_requested':
                case 'reschedule_responded': {
                    // Invalidar todas as queries de agendamento para forçar refetch
                    queryClient.invalidateQueries({ queryKey: ['instructor', 'schedule'] });
                    queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
                    queryClient.invalidateQueries({ queryKey: ['schedulings'] });
                    break;
                }
            }

            // Notificar listeners customizados (ex: hook de notificações)
            eventListenersRef.current.forEach((listener) => {
                try {
                    listener(message);
                } catch (error) {
                    console.error('[useWebSocket] Erro em event listener:', error);
                }
            });
        },
        [queryClient]
    );

    // =========================================================================
    // Conexão / Desconexão automática
    // =========================================================================

    useEffect(() => {
        if (!isAuthenticated) {
            wsService.disconnect();
            wsService.setTokenGetter(null);
            return;
        }

        // Configurar callback de status
        wsService.setStatusCallback(setStatus);

        // Configurar getter de token para que o WebSocket possa
        // obter tokens atualizados ao reconectar (ex: após refresh pelo Axios interceptor)
        const getValidToken = async (): Promise<string | null> => {
            try {
                // Buscar o token mais recente do SecureStore.
                // Se o interceptor do Axios já fez refresh, o token novo já estará lá.
                const token = await tokenManager.getAccessToken();
                return token;
            } catch (error) {
                console.error('[useWebSocket] Erro ao obter token:', error);
                return null;
            }
        };
        wsService.setTokenGetter(getValidToken);

        // Conectar com o token atual
        const connectAsync = async () => {
            const token = await tokenManager.getAccessToken();
            if (token) {
                wsService.connect(token);
            }
        };
        connectAsync();

        // Registrar handler de mensagens
        const unsubscribe = wsService.onMessage(handleMessage);

        return () => {
            unsubscribe();
            wsService.setStatusCallback(null);
            wsService.setTokenGetter(null);
        };
    }, [isAuthenticated, setStatus, handleMessage]);

    // =========================================================================
    // API pública do hook
    // =========================================================================

    /**
     * Envia dados via WebSocket.
     */
    const send = useCallback((data: object) => {
        wsService.send(data);
    }, []);

    /**
     * Registra um listener para eventos do WebSocket.
     * Retorna uma função de unsubscribe.
     *
     * Útil para hooks como useSchedulingNotifications que
     * querem reagir a eventos específicos (ex: mostrar Alert).
     */
    const onEvent = useCallback((callback: MessageCallback): (() => void) => {
        eventListenersRef.current.add(callback);
        return () => {
            eventListenersRef.current.delete(callback);
        };
    }, []);

    return {
        send,
        onEvent,
        isConnected,
    };
}
