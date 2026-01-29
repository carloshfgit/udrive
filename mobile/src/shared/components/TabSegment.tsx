import React from 'react';
import { View, TouchableOpacity, Text, ViewProps } from 'react-native';

interface TabSegmentOption {
    value: string;
    label: string;
}

interface TabSegmentProps extends ViewProps {
    options: TabSegmentOption[];
    value: string;
    onChange: (value: string) => void;
    className?: string;
}

export function TabSegment({
    options,
    value,
    onChange,
    className = '',
    style,
    ...props
}: TabSegmentProps) {
    return (
        <View
            className={`flex-row bg-neutral-100 p-1 rounded-xl ${className}`}
            style={style}
            {...props}
        >
            {options.map((option) => {
                const isSelected = value === option.value;

                return (
                    <TouchableOpacity
                        key={option.value}
                        onPress={() => onChange(option.value)}
                        className={`
              flex-1 items-center justify-center py-2 rounded-lg 
              ${isSelected ? 'bg-white shadow-sm' : 'bg-transparent'}
            `}
                        activeOpacity={0.7}
                    >
                        <Text
                            className={`
                text-sm font-semibold
                ${isSelected ? 'text-primary-600' : 'text-neutral-500'}
              `}
                        >
                            {option.label}
                        </Text>
                    </TouchableOpacity>
                );
            })}
        </View>
    );
}
