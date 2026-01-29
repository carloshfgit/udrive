import React from 'react';
import { TouchableOpacity, Text, TouchableOpacityProps } from 'react-native';

interface FilterChipProps extends TouchableOpacityProps {
    label: string;
    selected?: boolean;
    onPress: () => void;
    className?: string;
}

export function FilterChip({
    label,
    selected = false,
    onPress,
    className = '',
    style,
    ...props
}: FilterChipProps) {
    return (
        <TouchableOpacity
            onPress={onPress}
            activeOpacity={0.7}
            className={`
        px-4 py-2 rounded-full border mr-2
        ${selected
                    ? 'bg-primary-500 border-primary-500'
                    : 'bg-white border-neutral-200'
                }
        ${className}
      `}
            style={style}
            {...props}
        >
            <Text
                className={`
          text-sm font-medium
          ${selected ? 'text-white' : 'text-neutral-700'}
        `}
            >
                {label}
            </Text>
        </TouchableOpacity>
    );
}
