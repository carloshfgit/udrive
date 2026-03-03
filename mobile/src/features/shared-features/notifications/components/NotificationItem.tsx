/**
 * NotificationItem Component
 *
 * Card individual de notificação com ícone por tipo,
 * título, body, timestamp relativo e destaque visual para não-lidas.
 */

import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import {
    Calendar,
    MessageSquare,
    Star,
    CreditCard,
    Bell,
    RefreshCw,
} from 'lucide-react-native';
import type { NotificationResponse, NotificationType } from '../types/notification.types';

interface NotificationItemProps {
    notification: NotificationResponse;
    onPress: (notification: NotificationResponse) => void;
}

/**
 * Retorna ícone e cor baseados no tipo de notificação.
 */
function getNotificationMeta(type: NotificationType) {
    switch (type) {
        case 'NEW_SCHEDULING':
        case 'SCHEDULING_STATUS_CHANGED':
            return { icon: Calendar, color: '#2563EB', bgColor: '#EFF6FF' };
        case 'RESCHEDULE_REQUESTED':
        case 'RESCHEDULE_RESPONDED':
            return { icon: RefreshCw, color: '#D97706', bgColor: '#FFFBEB' };
        case 'NEW_CHAT_MESSAGE':
            return { icon: MessageSquare, color: '#059669', bgColor: '#ECFDF5' };
        case 'LESSON_REMINDER':
            return { icon: Bell, color: '#7C3AED', bgColor: '#F5F3FF' };
        case 'PAYMENT_STATUS_CHANGED':
            return { icon: CreditCard, color: '#2563EB', bgColor: '#EFF6FF' };
        case 'REVIEW_REQUEST':
            return { icon: Star, color: '#F59E0B', bgColor: '#FFFBEB' };
        default:
            return { icon: Bell, color: '#6B7280', bgColor: '#F3F4F6' };
    }
}

/**
 * Formata timestamp em formato relativo ("há 5 min", "há 2h", "há 3 dias").
 */
function formatRelativeTime(dateString: string): string {
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMin < 1) return 'agora';
    if (diffMin < 60) return `há ${diffMin} min`;
    if (diffHours < 24) return `há ${diffHours}h`;
    if (diffDays < 7) return `há ${diffDays}d`;
    if (diffDays < 30) return `há ${Math.floor(diffDays / 7)} sem`;

    return date.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' });
}

export function NotificationItem({ notification, onPress }: NotificationItemProps) {
    const { icon: Icon, color, bgColor } = getNotificationMeta(notification.type);

    return (
        <TouchableOpacity
            onPress={() => onPress(notification)}
            activeOpacity={0.7}
            className={`flex-row items-start px-5 py-4 ${notification.is_read ? 'bg-white' : 'bg-blue-50/50'
                }`}
        >
            {/* Ícone */}
            <View
                className="w-10 h-10 rounded-xl items-center justify-center mr-3 mt-0.5"
                style={{ backgroundColor: bgColor }}
            >
                <Icon size={20} color={color} />
            </View>

            {/* Conteúdo */}
            <View className="flex-1">
                <View className="flex-row items-center justify-between mb-0.5">
                    <Text
                        className={`text-sm flex-1 mr-2 ${notification.is_read
                                ? 'font-medium text-neutral-800'
                                : 'font-bold text-neutral-900'
                            }`}
                        numberOfLines={1}
                    >
                        {notification.title}
                    </Text>
                    <Text className="text-xs text-neutral-400">
                        {formatRelativeTime(notification.created_at)}
                    </Text>
                </View>

                <Text
                    className="text-xs text-neutral-500 leading-4"
                    numberOfLines={2}
                >
                    {notification.body}
                </Text>
            </View>

            {/* Indicador de não lida */}
            {!notification.is_read && (
                <View className="w-2 h-2 rounded-full bg-blue-500 ml-2 mt-2" />
            )}
        </TouchableOpacity>
    );
}
