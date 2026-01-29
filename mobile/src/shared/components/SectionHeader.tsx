import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';

interface SectionHeaderProps {
    title: string;
    actionLabel?: string;
    onAction?: () => void;
    className?: string;
}

export function SectionHeader({
    title,
    actionLabel = 'Ver tudo',
    onAction,
    className = '',
}: SectionHeaderProps) {
    return (
        <View className={`flex-row items-center justify-between mb-4 ${className}`}>
            <Text className="text-lg font-bold text-neutral-900">{title}</Text>

            {onAction && (
                <TouchableOpacity
                    onPress={onAction}
                    activeOpacity={0.7}
                    className="py-1 px-2 -mr-2"
                >
                    <Text className="text-sm font-medium text-primary-600">
                        {actionLabel}
                    </Text>
                </TouchableOpacity>
            )}
        </View>
    );
}
