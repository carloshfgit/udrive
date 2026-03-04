/**
 * ChatBubble Component
 *
 * Balão de mensagem individual no estilo WhatsApp.
 * Azul (primário) para enviadas, cinza claro para recebidas.
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import * as WebBrowser from 'expo-web-browser';
import { colors, radius, spacing, typography } from '../../../../shared/theme';

interface ChatBubbleProps {
    content: string;
    timestamp: string;
    isMine: boolean;
    isRead: boolean;
}

export const ChatBubble = ({ content, timestamp, isMine, isRead }: ChatBubbleProps) => {
    const formattedTime = format(new Date(timestamp), 'HH:mm', { locale: ptBR });

    const handlePress = async () => {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const match = content.match(urlRegex);
        if (match) {
            await WebBrowser.openBrowserAsync(match[0]);
        }
    };

    const isLink = /(https?:\/\/[^\s]+)/g.test(content);

    return (
        <View
            style={[
                styles.row,
                isMine ? styles.rowMine : styles.rowOther,
            ]}
        >
            <View
                style={[
                    styles.bubble,
                    isMine ? styles.bubbleMine : styles.bubbleOther,
                ]}
            >
                <Text
                    style={[
                        styles.content,
                        isMine ? styles.contentMine : styles.contentOther,
                        isLink && styles.linkText,
                    ]}
                    onPress={isLink ? handlePress : undefined}
                >
                    {content}
                </Text>

                <View style={styles.footer}>
                    <Text
                        style={[
                            styles.time,
                            isMine ? styles.timeMine : styles.timeOther,
                        ]}
                    >
                        {formattedTime}
                    </Text>

                    {isMine && (
                        <Text
                            style={[
                                styles.readIndicator,
                                isRead ? styles.readIndicatorRead : styles.readIndicatorUnread,
                            ]}
                        >
                            ✓✓
                        </Text>
                    )}
                </View>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    row: {
        paddingHorizontal: spacing.md,
        marginVertical: 2,
    },
    rowMine: {
        alignItems: 'flex-end',
    },
    rowOther: {
        alignItems: 'flex-start',
    },
    bubble: {
        maxWidth: '80%',
        paddingHorizontal: spacing.md,
        paddingTop: spacing.sm + 2,
        paddingBottom: spacing.xs + 2,
        borderRadius: radius.xl,
    },
    bubbleMine: {
        backgroundColor: colors.primary[100],
        borderBottomRightRadius: radius.sm,
    },
    bubbleOther: {
        backgroundColor: colors.primary[500],
        borderBottomLeftRadius: radius.sm,
    },
    content: {
        fontSize: typography.sizes.sm + 1,
        lineHeight: 20,
        fontFamily: typography.fontFamily.sans,
    },
    contentMine: {
        color: colors.text.primary,
    },
    contentOther: {
        color: colors.text.inverse,
    },
    linkText: {
        textDecorationLine: 'underline',
    },
    footer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'flex-end',
        marginTop: 2,
        gap: 4,
    },
    time: {
        fontSize: typography.sizes.xs - 1,
        fontFamily: typography.fontFamily.sans,
    },
    timeMine: {
        color: 'rgba(0, 0, 0, 0.7)',
    },
    timeOther: {
        color: colors.neutral[200],
    },
    readIndicator: {
        fontSize: typography.sizes.xs - 1,
        fontFamily: typography.fontFamily.semibold,
    },
    readIndicatorRead: {
        color: '#5bd13bff',
    },
    readIndicatorUnread: {
        color: 'rgba(108, 108, 108, 0.5)',
    },
});
