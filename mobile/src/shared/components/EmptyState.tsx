import React from 'react';
import { View, Text, ViewProps } from 'react-native';

interface EmptyStateProps extends ViewProps {
    title: string;
    message?: string;
    icon?: React.ReactNode;
    action?: React.ReactNode;
    className?: string;
}

export function EmptyState({
    title,
    message,
    icon,
    action,
    className = '',
    style,
    ...props
}: EmptyStateProps) {
    return (
        <View
            className={`items-center justify-center py-12 px-6 ${className}`}
            style={style}
            {...props}
        >
            {icon && (
                <View className="bg-neutral-50 w-16 h-16 rounded-full items-center justify-center mb-4">
                    {icon}
                </View>
            )}

            <Text className="text-lg font-bold text-neutral-900 text-center mb-2">
                {title}
            </Text>

            {message && (
                <Text className="text-base text-neutral-500 text-center leading-6 mb-6">
                    {message}
                </Text>
            )}

            {action && (
                <View className="mt-2">
                    {action}
                </View>
            )}
        </View>
    );
}
