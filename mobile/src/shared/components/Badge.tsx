import React from 'react';
import { View, Text, ViewProps } from 'react-native';

export type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline' | 'secondary';

interface BadgeProps extends ViewProps {
    label: string;
    variant?: BadgeVariant;
    className?: string;
}

export function Badge({
    label,
    variant = 'default',
    className = '',
    style,
    ...props
}: BadgeProps) {
    const variantStyles = {
        default: 'bg-primary-50 text-primary-700 border-transparent',
        success: 'bg-success-50 text-success-700 border-transparent',
        warning: 'bg-warning-50 text-warning-700 border-transparent',
        error: 'bg-error-50 text-error-700 border-transparent',
        info: 'bg-info-50 text-info-700 border-transparent',
        secondary: 'bg-secondary-50 text-secondary-700 border-transparent',
        outline: 'bg-transparent border-neutral-200 text-neutral-600 border',
    };

    // Extract text color class for the Text component logic
    // NativeWind handles class merging on parents, but nested text colors
    // need to be on the Text element explicitly or inherited.
    // For simplicity with mapped styles:
    const containerClasses = variantStyles[variant].split(' ').filter(c => !c.startsWith('text-')).join(' ');
    const textClasses = variantStyles[variant].split(' ').find(c => c.startsWith('text-')) || 'text-primary-700';

    return (
        <View
            className={`self-start rounded-full px-2.5 py-0.5 border ${containerClasses} ${className}`}
            style={style}
            {...props}
        >
            <Text className={`text-xs font-medium ${textClasses}`}>
                {label}
            </Text>
        </View>
    );
}
