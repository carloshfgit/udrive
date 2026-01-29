import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity, Modal, Dimensions, StyleSheet } from 'react-native';
import Animated, {
    useSharedValue,
    useAnimatedStyle,
    withSpring,
    withTiming,
    runOnJS
} from 'react-native-reanimated';
import { GestureDetector, Gesture, GestureHandlerRootView } from 'react-native-gesture-handler';

interface BottomSheetProps {
    isVisible: boolean;
    onClose: () => void;
    title?: string;
    children: React.ReactNode;
    snapPoints?: number[]; // Percentage of screen height, e.g. [50]
}

const { height: SCREEN_HEIGHT } = Dimensions.get('window');

export function BottomSheet({
    isVisible,
    onClose,
    title,
    children
}: BottomSheetProps) {
    const translateY = useSharedValue(SCREEN_HEIGHT);
    const opacity = useSharedValue(0);

    const active = isVisible;

    useEffect(() => {
        if (active) {
            translateY.value = withSpring(0, { damping: 50 });
            opacity.value = withTiming(0.5);
        } else {
            translateY.value = withTiming(SCREEN_HEIGHT, undefined, () => {
                // Cleanup if needed
            });
            opacity.value = withTiming(0);
        }
    }, [active]);

    const animatedStyle = useAnimatedStyle(() => ({
        transform: [{ translateY: translateY.value }],
    }));

    const backdropStyle = useAnimatedStyle(() => ({
        opacity: opacity.value,
    }));

    if (!isVisible) return null;

    return (
        <Modal transparent visible={isVisible} animationType="none" onRequestClose={onClose}>
            <View className="flex-1 justify-end">
                {/* Backdrop */}
                <TouchableOpacity
                    className="absolute inset-0 bg-black"
                    activeOpacity={1}
                    onPress={onClose}
                >
                    <Animated.View style={[{ flex: 1, backgroundColor: 'black' }, backdropStyle]} />
                </TouchableOpacity>

                {/* Content */}
                <Animated.View
                    style={[
                        {
                            backgroundColor: 'white',
                            borderTopLeftRadius: 24,
                            borderTopRightRadius: 24,
                            padding: 24,
                            minHeight: 200,
                            maxHeight: SCREEN_HEIGHT * 0.9,
                        },
                        animatedStyle
                    ]}
                >
                    {/* Handle Bar */}
                    <View className="items-center mb-6">
                        <View className="w-12 h-1.5 bg-neutral-200 rounded-full" />
                    </View>

                    {title && (
                        <View className="flex-row justify-between items-center mb-6">
                            <Text className="text-xl font-bold text-neutral-900">{title}</Text>
                            <TouchableOpacity onPress={onClose}>
                                <Text className="text-neutral-400 font-bold">✕</Text>
                            </TouchableOpacity>
                        </View>
                    )}

                    {children}
                </Animated.View>
            </View>
        </Modal>
    );
}
