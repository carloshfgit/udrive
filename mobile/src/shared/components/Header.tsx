/**
 * Header Component
 *
 * Header de navegação com título centralizado e botão voltar.
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ViewStyle } from 'react-native';

interface HeaderProps {
    /** Título do header */
    title: string;
    /** Callback do botão voltar */
    onBack?: () => void;
    /** Mostrar botão voltar */
    showBack?: boolean;
    /** Estilo customizado */
    style?: ViewStyle;
}

export function Header({
    title,
    onBack,
    showBack = true,
    style,
}: HeaderProps) {
    return (
        <View style={[styles.container, style]}>
            {showBack ? (
                <TouchableOpacity
                    onPress={onBack}
                    style={styles.backButton}
                    accessibilityLabel="Voltar"
                    accessibilityRole="button"
                    hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                >
                    <Text style={styles.backIcon}>‹</Text>
                </TouchableOpacity>
            ) : (
                <View style={styles.placeholder} />
            )}

            <Text style={styles.title}>{title}</Text>

            {/* Placeholder para manter o título centralizado */}
            <View style={styles.placeholder} />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: 16,
        paddingVertical: 12,
        backgroundColor: '#ffffff',
    },
    backButton: {
        width: 48,
        height: 48,
        justifyContent: 'center',
        alignItems: 'flex-start',
    },
    backIcon: {
        fontSize: 32,
        color: '#111318',
        fontWeight: '300',
    },
    title: {
        fontSize: 18,
        fontWeight: '700',
        color: '#111318',
        textAlign: 'center',
        flex: 1,
    },
    placeholder: {
        width: 48,
    },
});
