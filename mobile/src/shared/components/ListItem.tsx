import React from 'react';
import { View, Text, TouchableOpacity, ViewProps, TouchableOpacityProps } from 'react-native';

interface ListItemProps extends TouchableOpacityProps {
    title: string;
    subtitle?: string;
    leftIcon?: React.ReactNode;
    rightElement?: React.ReactNode;
    onPress?: () => void;
    showChevron?: boolean;
    className?: string;
}

export function ListItem({
    title,
    subtitle,
    leftIcon,
    rightElement,
    onPress,
    showChevron = true,
    className = '',
    style,
    ...props
}: ListItemProps) {
    if (onPress) {
        return (
            <TouchableOpacity
                className={`flex-row items-center py-4 border-b border-neutral-100 ${className}`}
                onPress={onPress}
                activeOpacity={0.7}
                style={style}
                {...props}
            >
                {/* Left Icon Slot */}
                {leftIcon && (
                    <View className="mr-4 w-10 h-10 bg-neutral-50 rounded-full items-center justify-center text-primary-600">
                        {leftIcon}
                    </View>
                )}

                {/* Content */}
                <View className="flex-1 justify-center">
                    <Text className="text-base font-medium text-neutral-900 leading-tight">
                        {title}
                    </Text>
                    {subtitle && (
                        <Text className="text-sm text-neutral-500 mt-1 leading-tight">
                            {subtitle}
                        </Text>
                    )}
                </View>

                {/* Right Element / Chevron */}
                <View className="flex-row items-center ml-2">
                    {rightElement}

                    {showChevron && !rightElement && (
                        <Text className="text-neutral-400 text-xl ml-2 font-light">›</Text>
                    )}
                </View>
            </TouchableOpacity>
        );
    }

    return (
        <View
            className={`flex-row items-center py-4 border-b border-neutral-100 ${className}`}
            style={style}
            {...props}
        >
            {/* Left Icon Slot */}
            {leftIcon && (
                <View className="mr-4 w-10 h-10 bg-neutral-50 rounded-full items-center justify-center text-primary-600">
                    {leftIcon}
                </View>
            )}

            {/* Content */}
            <View className="flex-1 justify-center">
                <Text className="text-base font-medium text-neutral-900 leading-tight">
                    {title}
                </Text>
                {subtitle && (
                    <Text className="text-sm text-neutral-500 mt-1 leading-tight">
                        {subtitle}
                    </Text>
                )}
            </View>

            {/* Right Element / Chevron */}
            <View className="flex-row items-center ml-2">
                {rightElement}
            </View>
        </View>
    );
}
