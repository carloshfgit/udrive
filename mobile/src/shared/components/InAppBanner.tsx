/**
 * InAppBanner
 *
 * Componente de notificação banner que aparece no topo da tela
 * com animação slide-in/slide-out. Suporta:
 * - Auto-dismiss após 4 segundos
 * - Swipe-to-dismiss (para cima)
 * - Navegação ao toque via useNotificationNavigation
 *
 * Deve ser renderizado globalmente no RootNavigator,
 * sobre todo o conteúdo de navegação.
 */

import React, { useEffect, useRef, useCallback } from 'react';
import {
    Animated,
    PanResponder,
    TouchableOpacity,
    View,
    Text,
    StyleSheet,
    Platform,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import {
    CalendarDays,
    MessageSquare,
    RefreshCw,
    Bell,
    X,
} from 'lucide-react-native';
import { useInAppBannerStore, InAppBannerType } from '../stores/inAppBannerStore';
import { useNotificationNavigation } from '../hooks/useNotificationNavigation';
import { colors, spacing, radius, typography } from '../theme';

// Tempo de exibição antes do auto-dismiss (ms)
const AUTO_DISMISS_DURATION = 4000;
// Duração da animação de entrada/saída (ms)
const ANIMATION_DURATION = 300;
// Limite de swipe para dismiss (px)
const SWIPE_THRESHOLD = -40;

// Configuração visual por tipo de banner
const BANNER_CONFIG: Record<InAppBannerType, {
    icon: typeof CalendarDays;
    accentColor: string;
    iconColor: string;
    backgroundColor: string;
}> = {
    scheduling: {
        icon: CalendarDays,
        accentColor: colors.primary[500],
        iconColor: colors.primary[500],
        backgroundColor: colors.primary[50],
    },
    chat: {
        icon: MessageSquare,
        accentColor: colors.success[500],
        iconColor: colors.success[500],
        backgroundColor: '#f0fdf4', // success-50 equivalent
    },
    reschedule: {
        icon: RefreshCw,
        accentColor: colors.warning[500],
        iconColor: colors.warning[500],
        backgroundColor: '#fffbeb', // warning-50 equivalent
    },
    info: {
        icon: Bell,
        accentColor: colors.info[500],
        iconColor: colors.info[500],
        backgroundColor: colors.primary[50],
    },
};

export function InAppBanner() {
    const currentBanner = useInAppBannerStore((s) => s.currentBanner);
    const dismiss = useInAppBannerStore((s) => s.dismiss);
    const { handleNotificationPress } = useNotificationNavigation();

    const translateY = useRef(new Animated.Value(-200)).current;
    const opacity = useRef(new Animated.Value(0)).current;
    const dismissTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const isAnimatingOut = useRef(false);

    // Limpar timer ao desmontar
    useEffect(() => {
        return () => {
            if (dismissTimer.current) {
                clearTimeout(dismissTimer.current);
            }
        };
    }, []);

    // Animação de saída
    const animateOut = useCallback(() => {
        if (isAnimatingOut.current) return;
        isAnimatingOut.current = true;

        if (dismissTimer.current) {
            clearTimeout(dismissTimer.current);
            dismissTimer.current = null;
        }

        Animated.parallel([
            Animated.timing(translateY, {
                toValue: -200,
                duration: ANIMATION_DURATION,
                useNativeDriver: true,
            }),
            Animated.timing(opacity, {
                toValue: 0,
                duration: ANIMATION_DURATION,
                useNativeDriver: true,
            }),
        ]).start(() => {
            isAnimatingOut.current = false;
            dismiss();
        });
    }, [dismiss, translateY, opacity]);

    // Animação de entrada quando o banner muda
    useEffect(() => {
        if (!currentBanner) {
            // Reset position para o próximo banner
            translateY.setValue(-200);
            opacity.setValue(0);
            return;
        }

        isAnimatingOut.current = false;

        // Animar entrada
        Animated.parallel([
            Animated.spring(translateY, {
                toValue: 0,
                tension: 80,
                friction: 12,
                useNativeDriver: true,
            }),
            Animated.timing(opacity, {
                toValue: 1,
                duration: ANIMATION_DURATION,
                useNativeDriver: true,
            }),
        ]).start();

        // Auto-dismiss timer
        dismissTimer.current = setTimeout(() => {
            animateOut();
        }, AUTO_DISMISS_DURATION);

        return () => {
            if (dismissTimer.current) {
                clearTimeout(dismissTimer.current);
                dismissTimer.current = null;
            }
        };
    }, [currentBanner?.id]); // eslint-disable-line react-hooks/exhaustive-deps

    // PanResponder para swipe-to-dismiss
    const panResponder = useRef(
        PanResponder.create({
            onStartShouldSetPanResponder: () => false,
            onMoveShouldSetPanResponder: (_, gestureState) => {
                // Capturar apenas swipes verticais para cima
                return gestureState.dy < -10 && Math.abs(gestureState.dy) > Math.abs(gestureState.dx);
            },
            onPanResponderMove: (_, gestureState) => {
                if (gestureState.dy < 0) {
                    translateY.setValue(gestureState.dy);
                }
            },
            onPanResponderRelease: (_, gestureState) => {
                if (gestureState.dy < SWIPE_THRESHOLD) {
                    animateOut();
                } else {
                    // Voltar à posição original
                    Animated.spring(translateY, {
                        toValue: 0,
                        tension: 80,
                        friction: 12,
                        useNativeDriver: true,
                    }).start();
                }
            },
        })
    ).current;

    // Handler de toque — navegar para o destino
    const handlePress = useCallback(() => {
        if (!currentBanner?.actionType || !currentBanner?.actionId) {
            animateOut();
            return;
        }

        // Dismiss imediato antes de navegar
        if (dismissTimer.current) {
            clearTimeout(dismissTimer.current);
            dismissTimer.current = null;
        }

        // Navegar usando a lógica existente de deep linking
        handleNotificationPress({
            type: currentBanner.notificationType || '',
            action_type: currentBanner.actionType,
            action_id: currentBanner.actionId,
            title: currentBanner.title,
            body: currentBanner.body,
        });

        animateOut();
    }, [currentBanner, handleNotificationPress, animateOut]);

    const insets = useSafeAreaInsets();

    if (!currentBanner) return null;

    const config = BANNER_CONFIG[currentBanner.type] || BANNER_CONFIG.info;
    const IconComponent = config.icon;

    return (
        <Animated.View
            {...panResponder.panHandlers}
            style={[
                styles.container,
                {
                    paddingTop: insets.top + spacing.xs,
                    transform: [{ translateY }],
                    opacity,
                },
            ]}
            pointerEvents="box-none"
        >
            <TouchableOpacity
                onPress={handlePress}
                activeOpacity={0.9}
                style={styles.touchable}
            >
                {/* Barra de acento colorida no topo */}
                <View style={[styles.accentBar, { backgroundColor: config.accentColor }]} />

                <View style={[styles.content, { backgroundColor: config.backgroundColor }]}>
                    {/* Ícone */}
                    <View style={[styles.iconContainer, { backgroundColor: config.accentColor + '1A' }]}>
                        <IconComponent size={20} color={config.iconColor} />
                    </View>

                    {/* Texto */}
                    <View style={styles.textContainer}>
                        <Text style={styles.title} numberOfLines={1}>
                            {currentBanner.title}
                        </Text>
                        <Text style={styles.body} numberOfLines={1}>
                            {currentBanner.body}
                        </Text>
                    </View>

                    {/* Botão de fechar */}
                    <TouchableOpacity
                        onPress={animateOut}
                        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                        style={styles.closeButton}
                    >
                        <X size={16} color={colors.neutral[400]} />
                    </TouchableOpacity>
                </View>
            </TouchableOpacity>
        </Animated.View>
    );
}

const styles = StyleSheet.create({
    container: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        paddingHorizontal: spacing.md,
    },
    touchable: {
        borderRadius: radius.lg,
        overflow: 'hidden',
        ...Platform.select({
            ios: {
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 4 },
                shadowOpacity: 0.15,
                shadowRadius: 12,
            },
            android: {
                elevation: 8,
            },
        }),
    },
    accentBar: {
        height: 3,
        width: '100%',
    },
    content: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: spacing.sm + 2,
        paddingHorizontal: spacing.md,
        gap: spacing.sm + 4,
    },
    iconContainer: {
        width: 40,
        height: 40,
        borderRadius: radius.xl,
        alignItems: 'center',
        justifyContent: 'center',
    },
    textContainer: {
        flex: 1,
        gap: 2,
    },
    title: {
        fontSize: typography.sizes.sm,
        fontFamily: typography.fontFamily.bold,
        color: colors.text.primary,
    },
    body: {
        fontSize: typography.sizes.xs,
        fontFamily: typography.fontFamily.sans,
        color: colors.text.secondary,
    },
    closeButton: {
        padding: spacing.xs,
    },
});
