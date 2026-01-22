/**
 * Button Component
 *
 * Botão reutilizável com variantes de estilo.
 */

import React from 'react';
import {
    TouchableOpacity,
    Text,
    ActivityIndicator,
    StyleSheet,
    ViewStyle,
    TextStyle,
} from 'react-native';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
    title: string;
    onPress: () => void;
    variant?: ButtonVariant;
    size?: ButtonSize;
    disabled?: boolean;
    loading?: boolean;
    fullWidth?: boolean;
    style?: ViewStyle;
    textStyle?: TextStyle;
}

export function Button({
    title,
    onPress,
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    fullWidth = false,
    style,
    textStyle,
}: ButtonProps) {
    const isDisabled = disabled || loading;

    return (
        <TouchableOpacity
            onPress={onPress}
            disabled={isDisabled}
            style={[
                styles.base,
                styles[variant],
                styles[`size_${size}`],
                fullWidth && styles.fullWidth,
                isDisabled && styles.disabled,
                style,
            ]}
            activeOpacity={0.7}
        >
            {loading ? (
                <ActivityIndicator
                    color={variant === 'primary' ? '#FFFFFF' : '#0ea5e9'}
                    size="small"
                />
            ) : (
                <Text
                    style={[
                        styles.text,
                        styles[`text_${variant}`],
                        styles[`text_${size}`],
                        textStyle,
                    ]}
                >
                    {title}
                </Text>
            )}
        </TouchableOpacity>
    );
}

const styles = StyleSheet.create({
    base: {
        borderRadius: 12,
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'row',
    },

    // Variantes
    primary: {
        backgroundColor: '#0ea5e9',
    },
    secondary: {
        backgroundColor: '#d946ef',
    },
    outline: {
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderColor: '#0ea5e9',
    },
    ghost: {
        backgroundColor: 'transparent',
    },

    // Tamanhos
    size_sm: {
        paddingVertical: 8,
        paddingHorizontal: 16,
        minHeight: 36,
    },
    size_md: {
        paddingVertical: 12,
        paddingHorizontal: 24,
        minHeight: 48,
    },
    size_lg: {
        paddingVertical: 16,
        paddingHorizontal: 32,
        minHeight: 56,
    },

    // Estados
    fullWidth: {
        width: '100%',
    },
    disabled: {
        opacity: 0.5,
    },

    // Texto base
    text: {
        fontWeight: '600',
    },

    // Texto por variante
    text_primary: {
        color: '#FFFFFF',
    },
    text_secondary: {
        color: '#FFFFFF',
    },
    text_outline: {
        color: '#0ea5e9',
    },
    text_ghost: {
        color: '#0ea5e9',
    },

    // Texto por tamanho
    text_sm: {
        fontSize: 14,
    },
    text_md: {
        fontSize: 16,
    },
    text_lg: {
        fontSize: 18,
    },
});
