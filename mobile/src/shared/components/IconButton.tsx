/**
 * IconButton Component
 *
 * Botão com ícone para ações como voltar ou login social.
 */

import React from 'react';
import {
    TouchableOpacity,
    Text,
    StyleSheet,
    ViewStyle,
} from 'react-native';

type IconButtonVariant = 'back' | 'social' | 'ghost';

interface IconButtonProps {
    /** Conteúdo do ícone (emoji, texto, ou componente React) */
    icon: React.ReactNode;
    /** Callback de clique */
    onPress: () => void;
    /** Variante do botão */
    variant?: IconButtonVariant;
    /** Tamanho do botão */
    size?: number;
    /** Label acessível */
    accessibilityLabel?: string;
    /** Desabilitado */
    disabled?: boolean;
    /** Estilo customizado */
    style?: ViewStyle;
}

export function IconButton({
    icon,
    onPress,
    variant = 'ghost',
    size = 48,
    accessibilityLabel,
    disabled = false,
    style,
}: IconButtonProps) {
    return (
        <TouchableOpacity
            onPress={onPress}
            disabled={disabled}
            accessibilityLabel={accessibilityLabel}
            accessibilityRole="button"
            style={[
                styles.base,
                styles[variant],
                { width: size, height: size },
                disabled && styles.disabled,
                style,
            ]}
            activeOpacity={0.7}
        >
            {typeof icon === 'string' ? (
                <Text style={styles.iconText}>{icon}</Text>
            ) : (
                icon
            )}
        </TouchableOpacity>
    );
}

const styles = StyleSheet.create({
    base: {
        justifyContent: 'center',
        alignItems: 'center',
        borderRadius: 12,
    },
    back: {
        backgroundColor: 'transparent',
    },
    social: {
        backgroundColor: '#ffffff',
        borderWidth: 1,
        borderColor: '#dbdfe6',
    },
    ghost: {
        backgroundColor: 'transparent',
    },
    disabled: {
        opacity: 0.5,
    },
    iconText: {
        fontSize: 24,
    },
});
