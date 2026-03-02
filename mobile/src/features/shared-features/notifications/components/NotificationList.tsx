/**
 * NotificationList Component
 *
 * FlatList com pull-to-refresh e paginação infinita
 * para exibir o histórico de notificações.
 */

import React from 'react';
import { FlatList, View, Text, ActivityIndicator, RefreshControl } from 'react-native';
import { Bell } from 'lucide-react-native';
import { NotificationItem } from './NotificationItem';
import type { NotificationResponse } from '../types/notification.types';

interface NotificationListProps {
    notifications: NotificationResponse[];
    isLoading: boolean;
    isFetchingNextPage: boolean;
    hasNextPage: boolean | undefined;
    onRefresh: () => void;
    onLoadMore: () => void;
    onPressNotification: (notification: NotificationResponse) => void;
}

function EmptyState() {
    return (
        <View className="flex-1 items-center justify-center py-20 px-8">
            <View className="w-16 h-16 rounded-2xl bg-neutral-100 items-center justify-center mb-4">
                <Bell size={28} color="#9CA3AF" />
            </View>
            <Text className="text-neutral-900 text-base font-bold mb-1">
                Nenhuma notificação
            </Text>
            <Text className="text-neutral-400 text-sm text-center">
                Quando você receber notificações sobre aulas, mensagens ou pagamentos, elas aparecerão aqui.
            </Text>
        </View>
    );
}

function ListFooter({ isFetchingNextPage }: { isFetchingNextPage: boolean }) {
    if (!isFetchingNextPage) return null;
    return (
        <View className="py-4 items-center">
            <ActivityIndicator size="small" color="#2563EB" />
        </View>
    );
}

function ItemSeparator() {
    return <View className="h-px bg-neutral-100 ml-18" />;
}

export function NotificationList({
    notifications,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    onRefresh,
    onLoadMore,
    onPressNotification,
}: NotificationListProps) {
    return (
        <FlatList
            data={notifications}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
                <NotificationItem
                    notification={item}
                    onPress={onPressNotification}
                />
            )}
            ItemSeparatorComponent={ItemSeparator}
            ListEmptyComponent={isLoading ? null : <EmptyState />}
            ListFooterComponent={<ListFooter isFetchingNextPage={isFetchingNextPage} />}
            refreshControl={
                <RefreshControl refreshing={isLoading} onRefresh={onRefresh} />
            }
            onEndReached={() => {
                if (hasNextPage && !isFetchingNextPage) {
                    onLoadMore();
                }
            }}
            onEndReachedThreshold={0.3}
            showsVerticalScrollIndicator={false}
            contentContainerStyle={
                notifications.length === 0 ? { flex: 1 } : undefined
            }
        />
    );
}
