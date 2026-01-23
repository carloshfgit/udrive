/**
 * Input Component
 *
 * Componente de input reutilizável com suporte a ícones.
 * Segue o design do GoDrive com altura de 56px e bordas arredondadas.
 */

import React from 'react';
import {
    View,
    TextInput,
    Text,
    StyleSheet,
    TextInputProps,
    ViewStyle,
} from 'react-native';

interface InputProps extends TextInputProps {
    /** Label do campo */
    label?: string;
    /** Ícone à esquerda (nome do Material Icon como emoji ou componente) */
    leftIcon?: React.ReactNode;
    /** Ícone à direita */
    rightIcon?: React.ReactNode;
    /** Mensagem de erro */
    error?: string;
    /** Estilo do container */
    containerStyle?: ViewStyle;
}

export function Input({
    label,
    leftIcon,
    rightIcon,
    error,
    containerStyle,
    style,
    ...props
}: InputProps) {
    const hasError = Boolean(error);

    return (
        <View style={[styles.container, containerStyle]}>
            {label && <Text style={styles.label}>{label}</Text>}

            <View
                style={[
                    styles.inputContainer,
                    hasError && styles.inputContainerError,
                ]}
            >
                {leftIcon && <View style={styles.leftIconContainer}>{leftIcon}</View>}

                <TextInput
                    style={[
                        styles.input,
                        leftIcon ? styles.inputWithLeftIcon : null,
                        rightIcon ? styles.inputWithRightIcon : null,
                        style,
                    ]}
                    placeholderTextColor="#616f89"
                    {...props}
                />

                {rightIcon && <View style={styles.rightIconContainer}>{rightIcon}</View>}
            </View>

            {error && <Text style={styles.errorText}>{error}</Text>}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        width: '100%',
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: '#111318',
        marginBottom: 8,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#ffffff',
        borderWidth: 1,
        borderColor: '#dbdfe6',
        borderRadius: 12,
        height: 56,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 1,
    },
    inputContainerError: {
        borderColor: '#ef4444',
    },
    leftIconContainer: {
        paddingLeft: 12,
        justifyContent: 'center',
        alignItems: 'center',
    },
    rightIconContainer: {
        paddingRight: 12,
        justifyContent: 'center',
        alignItems: 'center',
    },
    input: {
        flex: 1,
        height: '100%',
        fontSize: 16,
        color: '#111318',
        paddingHorizontal: 16,
    },
    inputWithLeftIcon: {
        paddingLeft: 8,
    },
    inputWithRightIcon: {
        paddingRight: 8,
    },
    errorText: {
        fontSize: 12,
        color: '#ef4444',
        marginTop: 4,
    },
});
