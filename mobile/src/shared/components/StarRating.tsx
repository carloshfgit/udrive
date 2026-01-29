import React from 'react';
import { View, Text, ViewProps } from 'react-native';

interface StarRatingProps extends ViewProps {
    rating: number; // 0 to 5
    showCount?: boolean;
    count?: number;
    size?: number; // font size for stars
    className?: string;
}

export function StarRating({
    rating,
    showCount = false,
    count,
    size = 14,
    className = '',
    style,
    ...props
}: StarRatingProps) {
    return (
        <View
            className={`flex-row items-center space-x-1 ${className}`}
            style={style}
            {...props}
        >
            <Text
                className="text-warning-500 font-bold"
                style={{ fontSize: size }}
            >
                ★
            </Text>
            <Text className="text-sm font-semibold text-neutral-900 ml-1">
                {rating.toFixed(1)}
            </Text>

            {showCount && count !== undefined && (
                <Text className="text-sm text-neutral-500 ml-1">
                    ({count} avaliações)
                </Text>
            )}
        </View>
    );
}
