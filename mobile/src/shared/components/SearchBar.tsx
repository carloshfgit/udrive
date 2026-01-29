import React from 'react';
import { View, TextInput, TouchableOpacity, TextInputProps, Text } from 'react-native';

interface SearchBarProps extends TextInputProps {
    onClear?: () => void;
    className?: string;
}

export function SearchBar({
    value,
    onChangeText,
    onClear,
    className = '',
    placeholder = 'Buscar...',
    style,
    ...props
}: SearchBarProps) {
    return (
        <View
            className={`flex-row items-center bg-white border border-neutral-200 rounded-xl px-4 h-12 ${className}`}
            style={style}
        >
            {/* Search Icon (Simulated with Text emoji for now, usually Feather/Ionicons) */}
            <Text className="text-neutral-400 mr-2 text-lg">🔍</Text>

            <TextInput
                className="flex-1 text-base text-neutral-900 h-full"
                placeholder={placeholder}
                placeholderTextColor="#9CA3AF"
                value={value}
                onChangeText={onChangeText}
                {...props}
            />

            {value ? (
                <TouchableOpacity onPress={() => {
                    onChangeText?.('');
                    onClear?.();
                }}>
                    <View className="bg-neutral-200 rounded-full w-5 h-5 items-center justify-center">
                        <Text className="text-neutral-500 text-xs font-bold">✕</Text>
                    </View>
                </TouchableOpacity>
            ) : null}
        </View>
    );
}
