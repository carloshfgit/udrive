/**
 * useNotifications Hook
 *
 * React Query hook para listar notificações com paginação infinita,
 * e mutations para marcar como lida (individual e todas).
 */

import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getNotifications,
    markAsRead,
    markAllAsRead,
    clearReadNotifications
} from '../api/notificationsApi';
import { useNotificationStore } from '../stores/notificationStore';
import type { NotificationResponse } from '../types/notification.types';

const PAGE_SIZE = 20;

/**
 * Mutation para limpar todas as notificações já lidas.
 */
export function useClearReadNotifications() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: clearReadNotifications,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
        },
    });
}

/**
 * Hook para listar notificações com paginação infinita.
 */
export function useNotifications() {
    const query = useInfiniteQuery({
        queryKey: ['notifications'],
        queryFn: ({ pageParam = 0 }) => getNotifications(PAGE_SIZE, pageParam),
        getNextPageParam: (lastPage, allPages) => {
            const loaded = allPages.reduce(
                (acc, page) => acc + page.notifications.length,
                0
            );
            return loaded < lastPage.total ? loaded : undefined;
        },
        initialPageParam: 0,
    });

    // Achatar páginas em uma lista única
    const notifications: NotificationResponse[] =
        query.data?.pages.flatMap((page) => page.notifications) ?? [];

    return {
        ...query,
        notifications,
    };
}

/**
 * Mutation para marcar uma notificação como lida.
 * Atualiza cache otimisticamente.
 */
export function useMarkAsRead() {
    const queryClient = useQueryClient();
    const decrementUnread = useNotificationStore((s) => s.decrementUnread);

    return useMutation({
        mutationFn: markAsRead,
        onMutate: async (notificationId: string) => {
            // Cancelar refetches em andamento
            await queryClient.cancelQueries({ queryKey: ['notifications'] });

            // Snapshot para rollback
            const previous = queryClient.getQueryData(['notifications']);

            // Atualizar otimisticamente
            queryClient.setQueryData<any>(['notifications'], (old: any) => {
                if (!old?.pages) return old;
                return {
                    ...old,
                    pages: old.pages.map((page: any) => ({
                        ...page,
                        notifications: page.notifications.map(
                            (n: NotificationResponse) =>
                                n.id === notificationId
                                    ? { ...n, is_read: true, read_at: new Date().toISOString() }
                                    : n
                        ),
                    })),
                };
            });

            decrementUnread();

            return { previous };
        },
        onError: (_err, _vars, context) => {
            // Rollback em caso de erro
            if (context?.previous) {
                queryClient.setQueryData(['notifications'], context.previous);
            }
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['notifications-unread-count'] });
        },
    });
}

/**
 * Mutation para marcar todas as notificações como lidas.
 */
export function useMarkAllAsRead() {
    const queryClient = useQueryClient();
    const resetUnread = useNotificationStore((s) => s.resetUnread);

    return useMutation({
        mutationFn: markAllAsRead,
        onSuccess: () => {
            resetUnread();
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            queryClient.invalidateQueries({ queryKey: ['notifications-unread-count'] });
        },
    });
}
