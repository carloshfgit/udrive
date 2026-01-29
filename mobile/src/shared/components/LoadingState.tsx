import React, { useEffect } from 'react';
import { View, ViewProps, DimensionValue } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withRepeat,
    withTiming,
    Easing
} from 'react-native-reanimated';

interface SkeletonProps extends ViewProps {
    width?: DimensionValue;
    height?: number;
    borderRadius?: number;
    className?: string;
}

function Skeleton({
    width = '100%',
    height = 20,
    borderRadius = 8,
    className = '',
    style,
    ...props
}: SkeletonProps) {
    const opacity = useSharedValue(0.3);

    useEffect(() => {
        opacity.value = withRepeat(
            withTiming(0.7, { duration: 800, easing: Easing.inOut(Easing.ease) }),
            -1,
            true
        );
    }, []);

    const animatedStyle = useAnimatedStyle(() => ({
        opacity: opacity.value,
    }));

    return (
        <Animated.View
            className={`bg-neutral-200 ${className}`}
            style={[
                { width, height, borderRadius },
                animatedStyle,
                style
            ]}
            {...props}
        />
    );
}

export const LoadingState = {
    Skeleton,

    // Preset: ListItem Skeleton
    ListItem: () => (
        <View className="flex-row items-center py-4 border-b border-neutral-100">
            <Skeleton width={40} height={40} borderRadius={20} className="mr-4" />
            <View className="flex-1">
                <Skeleton width="60%" height={16} className="mb-2" />
                <Skeleton width="40%" height={12} />
            </View>
        </View>
    ),

    // Preset: Card Skeleton
    Card: () => (
        <View className="p-4 border border-neutral-200 rounded-2xl mb-4">
            <View className="flex-row items-center mb-4">
                <Skeleton width={48} height={48} borderRadius={24} className="mr-3" />
                <View>
                    <Skeleton width={120} height={16} className="mb-2" />
                    <Skeleton width={80} height={12} />
                </View>
            </View>
            <Skeleton width="100%" height={12} className="mb-2" />
            <Skeleton width="80%" height={12} />
        </View>
    )
};
