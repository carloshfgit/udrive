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
    className?: string; // Container className
    inputClassName?: string; // TextInput className
}

export function Input({
    label,
    leftIcon,
    rightIcon,
    error,
    containerStyle,
    className = '',
    inputClassName = '',
    style,
    ...props
}: InputProps) {
    const hasError = Boolean(error);

    return (
        <View className={`w-full ${className}`} style={containerStyle}>
            {label && (
                <Text className="text-sm font-semibold text-neutral-900 mb-2">
                    {label}
                </Text>
            )}

            <View
                className={`
                    flex-row items-center bg-white border rounded-xl h-14 shadow-sm
                    ${hasError ? 'border-error-500' : 'border-neutral-200'}
                `}
            >
                {leftIcon && (
                    <View className="pl-3 justify-center items-center">
                        {leftIcon}
                    </View>
                )}

                <TextInput
                    className={`
                        flex-1 h-full text-base text-neutral-900 px-4
                        ${leftIcon ? 'pl-2' : ''}
                        ${rightIcon ? 'pr-2' : ''}
                        ${inputClassName}
                    `}
                    placeholderTextColor="#9ca3af" // neutral-400
                    style={style}
                    {...props}
                />

                {rightIcon && (
                    <View className="pr-3 justify-center items-center">
                        {rightIcon}
                    </View>
                )}
            </View>

            {error && (
                <Text className="text-xs text-error-500 mt-1 ml-1">
                    {error}
                </Text>
            )}
        </View>
    );
}
