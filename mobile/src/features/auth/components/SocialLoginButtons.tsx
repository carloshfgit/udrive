/**
 * SocialLoginButtons Component
 *
 * Botões de login social (Google e Apple) - Placeholder para implementação futura.
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';

interface SocialLoginButtonsProps {
    /** Callback opcional quando Google é pressionado */
    onGooglePress?: () => void;
    /** Callback opcional quando Apple é pressionado */
    onApplePress?: () => void;
}

export function SocialLoginButtons({
    onGooglePress,
    onApplePress,
}: SocialLoginButtonsProps) {
    const handleGooglePress = () => {
        if (onGooglePress) {
            onGooglePress();
        } else {
            Alert.alert(
                'Em breve',
                'Login com Google será implementado em uma versão futura.'
            );
        }
    };

    const handleApplePress = () => {
        if (onApplePress) {
            onApplePress();
        } else {
            Alert.alert(
                'Em breve',
                'Login com Apple será implementado em uma versão futura.'
            );
        }
    };

    return (
        <View style={styles.container}>
            {/* Google Button */}
            <TouchableOpacity
                style={styles.socialButton}
                onPress={handleGooglePress}
                activeOpacity={0.7}
            >
                <Text style={styles.googleIcon}>G</Text>
            </TouchableOpacity>

            {/* Apple Button */}
            <TouchableOpacity
                style={styles.socialButton}
                onPress={handleApplePress}
                activeOpacity={0.7}
            >
                <Text style={styles.appleIcon}></Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        justifyContent: 'center',
        gap: 24,
        paddingHorizontal: 16,
    },
    socialButton: {
        width: 56,
        height: 56,
        borderRadius: 12,
        backgroundColor: '#ffffff',
        borderWidth: 1,
        borderColor: '#dbdfe6',
        justifyContent: 'center',
        alignItems: 'center',
    },
    googleIcon: {
        fontSize: 24,
        fontWeight: '700',
        color: '#4285F4',
    },
    appleIcon: {
        fontSize: 24,
        color: '#000000',
    },
});
