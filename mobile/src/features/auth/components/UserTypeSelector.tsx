/**
 * UserTypeSelector Component
 *
 * Componente toggle para selecionar tipo de usuário (Aluno/Instrutor).
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

interface UserTypeSelectorProps {
    /** Valor selecionado */
    value: 'student' | 'instructor';
    /** Callback de mudança */
    onChange: (value: 'student' | 'instructor') => void;
}

export function UserTypeSelector({ value, onChange }: UserTypeSelectorProps) {
    return (
        <View style={styles.container}>
            <TouchableOpacity
                style={[
                    styles.option,
                    value === 'student' && styles.optionSelected,
                ]}
                onPress={() => onChange('student')}
                activeOpacity={0.7}
            >
                <Text style={styles.optionIcon}>🎓</Text>
                <Text
                    style={[
                        styles.optionText,
                        value === 'student' && styles.optionTextSelected,
                    ]}
                >
                    Aluno
                </Text>
            </TouchableOpacity>

            <TouchableOpacity
                style={[
                    styles.option,
                    value === 'instructor' && styles.optionSelected,
                ]}
                onPress={() => onChange('instructor')}
                activeOpacity={0.7}
            >
                <Text style={styles.optionIcon}>🚗</Text>
                <Text
                    style={[
                        styles.optionText,
                        value === 'instructor' && styles.optionTextSelected,
                    ]}
                >
                    Instrutor
                </Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        gap: 12,
    },
    option: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: 16,
        paddingHorizontal: 16,
        backgroundColor: '#ffffff',
        borderWidth: 2,
        borderColor: '#dbdfe6',
        borderRadius: 12,
        gap: 8,
    },
    optionSelected: {
        backgroundColor: '#135bec',
        borderColor: '#135bec',
    },
    optionIcon: {
        fontSize: 20,
    },
    optionText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#111318',
    },
    optionTextSelected: {
        color: '#ffffff',
    },
});
