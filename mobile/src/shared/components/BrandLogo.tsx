/**
 * BrandLogo Component
 *
 * Componente de logo/branding do GoDrive.
 * Exibe o ícone do carro em círculo azul com texto abaixo.
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';

interface BrandLogoProps {
    /** Título abaixo do ícone */
    title?: string;
    /** Tamanho do ícone */
    iconSize?: 'sm' | 'md' | 'lg';
    /** Estilo customizado */
    style?: ViewStyle;
}

const iconSizes = {
    sm: { container: 48, icon: 24 },
    md: { container: 72, icon: 36 },
    lg: { container: 96, icon: 48 },
};

export function BrandLogo({
    title = 'GoDrive',
    iconSize = 'md',
    style,
}: BrandLogoProps) {
    const sizes = iconSizes[iconSize];

    return (
        <View style={[styles.container, style]}>
            <View style={styles.card}>
                <View
                    style={[
                        styles.iconCircle,
                        { width: sizes.container, height: sizes.container },
                    ]}
                >
                    <Text style={[styles.icon, { fontSize: sizes.icon }]}>🚗</Text>
                </View>
                <Text style={styles.title}>{title}</Text>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        paddingHorizontal: 16,
        paddingVertical: 24,
    },
    card: {
        backgroundColor: 'rgba(19, 91, 236, 0.1)',
        borderRadius: 16,
        borderWidth: 1,
        borderColor: 'rgba(19, 91, 236, 0.05)',
        paddingVertical: 24,
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 180,
    },
    iconCircle: {
        backgroundColor: '#135bec',
        borderRadius: 999,
        justifyContent: 'center',
        alignItems: 'center',
        shadowColor: '#135bec',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3,
        shadowRadius: 16,
        elevation: 8,
    },
    icon: {
        color: '#ffffff',
    },
    title: {
        marginTop: 12,
        fontSize: 20,
        fontWeight: '700',
        color: '#135bec',
    },
});
