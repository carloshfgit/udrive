/**
 * Notification Store (Zustand)
 *
 * Estado real-time das notificações, atualizado via WebSocket.
 * O unreadCount é sincronizado com o backend e atualizado
 * instantaneamente quando uma notificação chega via WS.
 */

import { create } from 'zustand';

interface NotificationState {
    /** Contagem de notificações não lidas */
    unreadCount: number;
}

interface NotificationActions {
    /** Define a contagem (sync com backend via React Query) */
    setUnreadCount: (count: number) => void;

    /** Incrementa em 1 (nova notificação via WebSocket) */
    incrementUnread: () => void;

    /** Decrementa em 1 (marcar uma como lida) */
    decrementUnread: () => void;

    /** Reseta para 0 (marcar todas como lidas) */
    resetUnread: () => void;
}

export const useNotificationStore = create<NotificationState & NotificationActions>((set) => ({
    unreadCount: 0,

    setUnreadCount: (count) => set({ unreadCount: count }),

    incrementUnread: () =>
        set((state) => ({ unreadCount: state.unreadCount + 1 })),

    decrementUnread: () =>
        set((state) => ({ unreadCount: Math.max(0, state.unreadCount - 1) })),

    resetUnread: () => set({ unreadCount: 0 }),
}));
