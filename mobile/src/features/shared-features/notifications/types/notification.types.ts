/**
 * GoDrive Mobile - Notification Types
 *
 * Tipos TypeScript para o sistema de notificações.
 */

// === Enums ===

export type NotificationType =
    | 'NEW_SCHEDULING'
    | 'RESCHEDULE_REQUESTED'
    | 'RESCHEDULE_RESPONDED'
    | 'NEW_CHAT_MESSAGE'
    | 'LESSON_REMINDER'
    | 'PAYMENT_STATUS_CHANGED'
    | 'SCHEDULING_STATUS_CHANGED'
    | 'REVIEW_REQUEST';

export type ActionType = 'SCHEDULING' | 'CHAT' | 'REVIEW' | 'PAYMENT';

// === Response DTOs ===

export interface NotificationResponse {
    id: string;
    type: NotificationType;
    title: string;
    body: string;
    action_type: ActionType | null;
    action_id: string | null;
    is_read: boolean;
    created_at: string;
    read_at: string | null;
}

export interface NotificationListResponse {
    notifications: NotificationResponse[];
    unread_count: number;
    total: number;
}

export interface UnreadCountResponse {
    count: number;
}
