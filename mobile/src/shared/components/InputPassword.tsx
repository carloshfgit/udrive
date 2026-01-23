/**
 * InputPassword Component
 *
 * Componente de input para senha com toggle de visibilidade.
 * Estende o Input base com ícone de cadeado e botão de mostrar/ocultar.
 */

import React, { useState } from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { Input } from './Input';
import type { TextInputProps, ViewStyle } from 'react-native';

interface InputPasswordProps extends Omit<TextInputProps, 'secureTextEntry'> {
    /** Label do campo */
    label?: string;
    /** Texto do link adicional (ex: "Esqueceu a senha?") */
    linkText?: string;
    /** Callback do link */
    onLinkPress?: () => void;
    /** Mensagem de erro */
    error?: string;
    /** Estilo do container */
    containerStyle?: ViewStyle;
}

export function InputPassword({
    label = 'Senha',
    linkText,
    onLinkPress,
    error,
    containerStyle,
    ...props
}: InputPasswordProps) {
    const [isVisible, setIsVisible] = useState(false);

    const toggleVisibility = () => {
        setIsVisible(!isVisible);
    };

    // Ícone de cadeado à esquerda
    const lockIcon = (
        <Text style={styles.icon}>🔒</Text>
    );

    // Ícone de visibilidade à direita
    const visibilityIcon = (
        <TouchableOpacity onPress={toggleVisibility} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
            <Text style={styles.icon}>{isVisible ? '👁️' : '👁️‍🗨️'}</Text>
        </TouchableOpacity>
    );

    // Label customizado com link opcional
    const customLabel = linkText ? (
        <Text style={styles.labelContainer}>
            <Text style={styles.label}>{label}</Text>
            {'                    '}
            <Text style={styles.link} onPress={onLinkPress}>
                {linkText}
            </Text>
        </Text>
    ) : (
        label
    );

    return (
        <Input
            label={typeof customLabel === 'string' ? customLabel : undefined}
            leftIcon={lockIcon}
            rightIcon={visibilityIcon}
            secureTextEntry={!isVisible}
            error={error}
            containerStyle={containerStyle}
            {...props}
        />
    );
}

const styles = StyleSheet.create({
    icon: {
        fontSize: 20,
        opacity: 0.6,
    },
    labelContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: '#111318',
    },
    link: {
        fontSize: 14,
        fontWeight: '500',
        color: '#135bec',
    },
});
