/**
 * ChatInput Component
 *
 * Barra de input para envio de mensagens.
 * Integra o filtro de mensagens proibidas antes de enviar.
 */

import React, { useState, useCallback } from 'react';
import {
    View,
    TextInput,
    TouchableOpacity,
    Text,
    StyleSheet,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { Send, MapPin } from 'lucide-react-native';
import * as Location from 'expo-location';
import { colors, radius, spacing, typography } from '../../../../shared/theme';
import { checkProhibitedContent } from '../utils/messageFilter';

interface ChatInputProps {
    onSend: (content: string) => Promise<void> | void;
    isSending?: boolean;
}

export function ChatInput({ onSend, isSending = false }: ChatInputProps) {
    const [text, setText] = useState('');
    const [warning, setWarning] = useState('');
    const [isGettingLocation, setIsGettingLocation] = useState(false);

    const handleSend = useCallback(async () => {
        const trimmed = text.trim();
        if (!trimmed || isSending) return;

        // Verificar conteúdo proibido
        const result = checkProhibitedContent(trimmed);
        if (result.isProhibited) {
            setWarning(result.reason);
            return;
        }

        setWarning('');
        setText('');
        await onSend(trimmed);
    }, [text, isSending, onSend]);

    const handleSendLocation = useCallback(async () => {
        if (isSending || isGettingLocation) return;

        try {
            setIsGettingLocation(true);
            const { status } = await Location.requestForegroundPermissionsAsync();

            if (status !== 'granted') {
                Alert.alert(
                    'Permissão Negada',
                    'Precisamos de permissão para acessar sua localização e enviar o link.'
                );
                return;
            }

            const location = await Location.getCurrentPositionAsync({
                accuracy: Location.Accuracy.Balanced,
            });

            const { latitude, longitude } = location.coords;
            const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`;

            await onSend(googleMapsUrl);
        } catch (error) {
            console.error('Erro ao obter localização:', error);
            Alert.alert('Erro', 'Não foi possível obter sua localização atual.');
        } finally {
            setIsGettingLocation(false);
        }
    }, [isSending, isGettingLocation, onSend]);

    const handleChangeText = useCallback((value: string) => {
        setText(value);
        // Limpar aviso quando o usuário edita o texto
        if (warning) setWarning('');
    }, [warning]);

    const canSend = text.trim().length > 0 && !isSending;

    return (
        <View style={styles.container}>
            {/* Aviso de mensagem proibida */}
            {warning !== '' && (
                <View style={styles.warningContainer}>
                    <Text style={styles.warningIcon}>⚠️</Text>
                    <Text style={styles.warningText}>{warning}</Text>
                </View>
            )}

            <View style={styles.inputRow}>
                <TouchableOpacity
                    style={styles.attachmentButton}
                    onPress={handleSendLocation}
                    disabled={isSending || isGettingLocation}
                    activeOpacity={0.7}
                >
                    {isGettingLocation ? (
                        <ActivityIndicator size="small" color={colors.primary[500]} />
                    ) : (
                        <MapPin size={22} color={colors.primary[500]} />
                    )}
                </TouchableOpacity>

                <TextInput
                    style={styles.input}
                    value={text}
                    onChangeText={handleChangeText}
                    placeholder="Digite uma mensagem..."
                    placeholderTextColor={colors.neutral[400]}
                    multiline
                    maxLength={1000}
                    editable={!isSending}
                />

                {canSend && (
                    <TouchableOpacity
                        style={styles.sendButton}
                        onPress={handleSend}
                        activeOpacity={0.7}
                        accessibilityLabel="Enviar mensagem"
                        accessibilityRole="button"
                    >
                        {isSending ? (
                            <ActivityIndicator size="small" color={colors.text.inverse} />
                        ) : (
                            <Send size={20} color={colors.text.inverse} />
                        )}
                    </TouchableOpacity>
                )}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        backgroundColor: colors.surface.light,
        borderTopWidth: 1,
        borderTopColor: colors.border.light,
        paddingHorizontal: spacing.md,
        paddingTop: spacing.sm,
        paddingBottom: spacing.sm + 28,
    },
    warningContainer: {
        flexDirection: 'row',
        alignItems: 'flex-start',
        backgroundColor: '#fef2f2',
        borderWidth: 1,
        borderColor: '#fecaca',
        borderRadius: radius.md,
        paddingHorizontal: spacing.sm + 4,
        paddingVertical: spacing.sm,
        marginBottom: spacing.sm,
        gap: 6,
    },
    warningIcon: {
        fontSize: 14,
        marginTop: 1,
    },
    warningText: {
        flex: 1,
        fontSize: typography.sizes.xs,
        fontFamily: typography.fontFamily.medium,
        color: colors.error[600],
        lineHeight: 18,
    },
    inputRow: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        gap: spacing.sm,
    },
    input: {
        flex: 1,
        backgroundColor: colors.neutral[50],
        borderWidth: 1,
        borderColor: colors.border.light,
        borderRadius: radius.xl,
        paddingHorizontal: spacing.md,
        paddingTop: spacing.sm + 2,
        paddingBottom: spacing.sm + 2,
        fontSize: typography.sizes.sm + 1,
        fontFamily: typography.fontFamily.sans,
        color: colors.text.primary,
        maxHeight: 100,
        minHeight: 42,
    },
    attachmentButton: {
        width: 42,
        height: 42,
        borderRadius: radius.full,
        backgroundColor: colors.neutral[100],
        justifyContent: 'center',
        alignItems: 'center',
    },
    sendButton: {
        width: 42,
        height: 42,
        borderRadius: radius.full,
        backgroundColor: colors.primary[500],
        justifyContent: 'center',
        alignItems: 'center',
    },
});
