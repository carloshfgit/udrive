import React from 'react';
import { View, Image, Text, TouchableOpacity, ImageSourcePropType } from 'react-native';

interface AvatarProps {
    source?: ImageSourcePropType | string;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    fallback?: string; // Initials or fallback character
    onEdit?: () => void; // If provided, shows camera badge
    className?: string;
}

export function Avatar({
    source,
    size = 'md',
    fallback = '?',
    onEdit,
    className = '',
}: AvatarProps) {
    const sizeClasses = {
        sm: 'w-8 h-8',
        md: 'w-12 h-12',
        lg: 'w-16 h-16',
        xl: 'w-24 h-24',
    };

    const textSizeClasses = {
        sm: 'text-xs',
        md: 'text-base',
        lg: 'text-xl',
        xl: 'text-3xl',
    };

    // Resolve source if it's a string URL
    const imageSource = typeof source === 'string' ? { uri: source } : source;

    return (
        <View className={`relative ${className}`}>
            <View
                className={`bg-neutral-200 rounded-full items-center justify-center overflow-hidden ${sizeClasses[size]}`}
            >
                {imageSource ? (
                    <Image
                        source={imageSource}
                        className="w-full h-full"
                        resizeMode="cover"
                    />
                ) : (
                    <Text className={`font-bold text-neutral-500 ${textSizeClasses[size]}`}>
                        {fallback.toUpperCase().slice(0, 2)}
                    </Text>
                )}
            </View>

            {/* Edit Badge */}
            {onEdit && (
                <TouchableOpacity
                    onPress={onEdit}
                    activeOpacity={0.8}
                    className="absolute bottom-0 right-0 bg-primary-500 border-2 border-white rounded-full p-1.5 items-center justify-center shadow-sm"
                >
                    {/* Simple Camera Icon (Text for now, replace with Icon later) */}
                    <Text className="text-white text-[10px] font-bold">📷</Text>
                </TouchableOpacity>
            )}
        </View>
    );
}
