import React from 'react';
import { View, ViewProps } from 'react-native';
import { cssInterop } from 'nativewind';

interface CardProps extends ViewProps {
    variant?: 'elevated' | 'outlined' | 'filled';
    className?: string;
    children?: React.ReactNode;
}

export function Card({
    variant = 'elevated',
    className = '',
    style,
    children,
    ...props
}: CardProps) {
    const baseClasses = 'rounded-2xl p-4';

    const variantClasses = {
        elevated: 'bg-white shadow-sm border border-neutral-100',
        outlined: 'bg-transparent border border-neutral-200',
        filled: 'bg-neutral-50 border-transparent',
    };

    return (
        <View
            className={`${baseClasses} ${variantClasses[variant]} ${className}`}
            style={style}
            {...props}
        >
            {children}
        </View>
    );
}
