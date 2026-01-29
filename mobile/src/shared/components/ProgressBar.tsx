import React, { useEffect } from 'react';
import { View, ViewProps } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withTiming
} from 'react-native-reanimated';

interface ProgressBarProps extends ViewProps {
    progress: number; // 0 to 100
    color?: string;
    height?: number;
    className?: string;
}

export function ProgressBar({
    progress,
    color, // Can be used for imperative color styles if needed, but classes preferred
    height = 8,
    className = '',
    style,
    ...props
}: ProgressBarProps) {
    const width = useSharedValue(0);

    useEffect(() => {
        width.value = withTiming(progress, { duration: 1000 });
    }, [progress]);

    const animatedStyle = useAnimatedStyle(() => {
        return {
            width: `${width.value}%`,
        };
    });

    return (
        <View
            className={`w-full bg-neutral-100 rounded-full overflow-hidden ${className}`}
            style={[{ height }, style]}
            {...props}
        >
            <Animated.View
                style={[
                    animatedStyle,
                    {
                        height: '100%',
                        borderRadius: height / 2,
                        backgroundColor: color || '#2563EB' // specific default or fallback
                    }
                ]}
                className={!color ? "bg-primary-500" : ""}
            />
        </View>
    );
}
