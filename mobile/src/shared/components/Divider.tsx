/**
 * Divider Component
 *
 * Divisor horizontal com texto central opcional.
 * Usado para separar seções como "Ou entre com".
 */

import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';

interface DividerProps {
    /** Texto central (opcional) */
    text?: string;
    /** Estilo do container */
    style?: ViewStyle;
}

export function Divider({ text, style }: DividerProps) {
    if (!text) {
        return <View style={[styles.line, style]} />;
    }

    return (
        <View style={[styles.container, style]}>
            <View style={styles.line} />
            <Text style={styles.text}>{text}</Text>
            <View style={styles.line} />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 24,
    },
    line: {
        flex: 1,
        height: 1,
        backgroundColor: '#dbdfe6',
    },
    text: {
        paddingHorizontal: 16,
        fontSize: 14,
        color: '#9ca3af',
    },
});
