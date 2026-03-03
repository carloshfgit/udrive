/**
 * NotificationsScreen
 *
 * Tela de histórico de notificações com header,
 * botão "Marcar todas como lidas", e lista paginada.
 */

import React from 'react';
import { View, Text, SafeAreaView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { ArrowLeft, CheckCheck, Trash2 } from 'lucide-react-native';
import { NotificationList } from '../components/NotificationList';
import { useNotifications, useMarkAsRead, useMarkAllAsRead, useClearReadNotifications } from '../hooks/useNotifications';
import { useNotificationNavigation } from '../../../../shared/hooks/useNotificationNavigation';
import type { NotificationResponse } from '../types/notification.types';

export function NotificationsScreen() {
    const navigation = useNavigation();
    const { handleNotificationPress } = useNotificationNavigation();

    const {
        notifications,
        isLoading,
        isFetchingNextPage,
        hasNextPage,
        refetch,
        fetchNextPage,
    } = useNotifications();

    const markAsRead = useMarkAsRead();
    const markAllAsRead = useMarkAllAsRead();
    const clearRead = useClearReadNotifications();

    const hasUnread = notifications.some((n) => !n.is_read);
    const hasRead = notifications.some((n) => n.is_read);

    function handlePressNotification(notification: NotificationResponse) {
        // Marcar como lida se ainda não foi
        if (!notification.is_read) {
            markAsRead.mutate(notification.id);
        }

        // Navegar para o destino (deep link)
        if (notification.action_type && notification.action_id) {
            handleNotificationPress({
                type: notification.type,
                action_type: notification.action_type,
                action_id: notification.action_id,
                title: notification.title,
                body: notification.body,
            });
        }
    }

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="flex-row items-center justify-between px-5 py-3 border-b border-neutral-100">
                <View className="flex-row items-center">
                    <TouchableOpacity
                        onPress={() => navigation.goBack()}
                        className="w-10 h-10 items-center justify-center rounded-xl mr-2"
                        activeOpacity={0.7}
                    >
                        <ArrowLeft size={22} color="#171717" />
                    </TouchableOpacity>
                    <Text className="text-neutral-900 text-lg font-bold">
                        Notificações
                    </Text>
                </View>

                <View className="flex-row items-center space-x-2">
                    {hasRead && (
                        <TouchableOpacity
                            onPress={() => clearRead.mutate()}
                            disabled={clearRead.isPending}
                            className="flex-row items-center px-3 py-2 rounded-lg bg-red-50 mr-2"
                            activeOpacity={0.7}
                        >
                            {clearRead.isPending ? (
                                <ActivityIndicator size="small" color="#DC2626" />
                            ) : (
                                <>
                                    <Trash2 size={16} color="#DC2626" />
                                    <Text className="text-red-600 text-xs font-semibold ml-1">
                                        Limpar
                                    </Text>
                                </>
                            )}
                        </TouchableOpacity>
                    )}

                    {hasUnread && (
                        <TouchableOpacity
                            onPress={() => markAllAsRead.mutate()}
                            disabled={markAllAsRead.isPending}
                            className="flex-row items-center px-3 py-2 rounded-lg bg-blue-50"
                            activeOpacity={0.7}
                        >
                            {markAllAsRead.isPending ? (
                                <ActivityIndicator size="small" color="#2563EB" />
                            ) : (
                                <>
                                    <CheckCheck size={16} color="#2563EB" />
                                    <Text className="text-blue-600 text-xs font-semibold ml-1">
                                        Ler todas
                                    </Text>
                                </>
                            )}
                        </TouchableOpacity>
                    )}
                </View>
            </View>

            {/* Lista */}
            <NotificationList
                notifications={notifications}
                isLoading={isLoading}
                isFetchingNextPage={isFetchingNextPage}
                hasNextPage={hasNextPage}
                onRefresh={() => refetch()}
                onLoadMore={() => fetchNextPage()}
                onPressNotification={handlePressNotification}
            />
        </SafeAreaView>
    );
}
