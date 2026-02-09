/**
 * Button Component
 *
 * Botão reutilizável com variantes de estilo via NativeWind.
 */

import React from 'react';
import {
    TouchableOpacity,
    Text,
    ActivityIndicator,
    View,
    ViewStyle,
    TextStyle,
} from 'react-native';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
    title: string;
    onPress: () => void;
    variant?: ButtonVariant;
    size?: ButtonSize;
    disabled?: boolean;
    loading?: boolean;
    fullWidth?: boolean;
    className?: string;
    textClassName?: string;
    style?: ViewStyle;
    textStyle?: TextStyle;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
}

export function Button({
    title,
    onPress,
    variant = 'primary',
    size = 'md',
    disabled = false,
    loading = false,
    fullWidth = false,
    className = '',
    textClassName = '',
    style,
    textStyle,
    leftIcon,
    rightIcon,
}: ButtonProps) {
    const isDisabled = disabled || loading;

    const variantStyles = {
        primary: 'bg-primary-500',
        secondary: 'bg-secondary-500',
        outline: 'bg-transparent border-2 border-primary-500',
        ghost: 'bg-transparent',
        danger: 'bg-error-500',
    };

    const sizeStyles = {
        sm: 'py-2 px-4 min-h-[36px]',
        md: 'py-3 px-6 min-h-[48px]',
        lg: 'py-4 px-8 min-h-[56px]',
    };

    const textVariantStyles = {
        primary: 'text-white',
        secondary: 'text-white',
        outline: 'text-primary-500',
        ghost: 'text-primary-500',
        danger: 'text-white',
    };

    const textSizeStyles = {
        sm: 'text-sm',
        md: 'text-base',
        lg: 'text-lg',
    };

    return (
        <TouchableOpacity
            onPress={onPress}
            disabled={isDisabled}
            activeOpacity={0.7}
            className={`
                rounded-xl items-center justify-center flex-row
                ${variantStyles[variant]}
                ${sizeStyles[size]}
                ${fullWidth ? 'w-full' : 'self-start'}
                ${isDisabled ? 'opacity-50' : ''}
                ${className}
            `}
            style={style}
        >
            {loading ? (
                <ActivityIndicator
                    color={variant === 'outline' || variant === 'ghost' ? '#135bec' : '#FFFFFF'}
                    size="small"
                />
            ) : (
                <>
                    {leftIcon && <View className="mr-2">{leftIcon}</View>}
                    <Text
                        className={`
                            font-semibold text-center
                            ${textVariantStyles[variant]}
                            ${textSizeStyles[size]}
                            ${textClassName}
                        `}
                        style={textStyle}
                    >
                        {title}
                    </Text>
                    {rightIcon && <View className="ml-2">{rightIcon}</View>}
                </>
            )}
        </TouchableOpacity>
    );
}
