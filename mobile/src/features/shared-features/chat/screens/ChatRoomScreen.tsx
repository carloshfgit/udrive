/**
 * ChatRoomScreen
 *
 * Tela de conversa individual entre dois usuários.
 * Comportamento de teclado estilo WhatsApp — header fixo,
 * mensagens e input acompanham o teclado.
 */

import React, { useCallback, useRef } from 'react';
import {
    View,
    FlatList,
    SafeAreaView,
    KeyboardAvoidingView,
    Platform,
    StyleSheet,
    Text,
    TouchableOpacity,
} from 'react-native';
import { useRoute, useNavigation, useFocusEffect } from '@react-navigation/native';
import { BookOpen, MapPin } from 'lucide-react-native';
import { useAuthStore } from '@lib/store';
import { Header } from '../../../../shared/components/Header';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { ChatBubble } from '../components/ChatBubble';
import { ChatInput } from '../components/ChatInput';
import { useMessages } from '../hooks/useMessages';
import { MessageResponse } from '../api/chatApi';
import { colors, spacing, typography } from '../../../../shared/theme';
import { useInAppBannerStore } from '../../../../shared/stores/inAppBannerStore';

export function ChatRoomScreen() {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { user } = useAuthStore();
    const flatListRef = useRef<FlatList>(null);
    const setChatScreenActive = useInAppBannerStore((s) => s.setChatScreenActive);

    // Suprimir banners de chat enquanto esta tela estiver focada
    useFocusEffect(
        React.useCallback(() => {
            setChatScreenActive(true);
            return () => setChatScreenActive(false);
        }, [setChatScreenActive])
    );

    const { otherUserId, otherUserName } = route.params;
    const { messages, sendMessage, isSending, isLoading } = useMessages(otherUserId);

    // Mensagens invertidas para FlatList invertida (mais recentes no topo)
    const sortedMessages = React.useMemo(() => {
        if (!messages) return [];
        return [...messages].sort(
            (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
    }, [messages]);

    const handleSend = useCallback(
        async (content: string) => {
            await sendMessage(content);
        },
        [sendMessage]
    );

    const handleViewLessons = useCallback(() => {
        navigation.navigate('StudentLessonHistory', {
            studentId: otherUserId,
            studentName: otherUserName,
        });
    }, [navigation, otherUserId, otherUserName]);

    const renderMessage = useCallback(
        ({ item }: { item: MessageResponse }) => (
            <ChatBubble
                content={item.content}
                timestamp={item.timestamp}
                isMine={item.sender_id === user?.id}
                isRead={item.is_read}
            />
        ),
        [user?.id]
    );

    const keyExtractor = useCallback((item: MessageResponse) => item.id, []);

    return (
        <SafeAreaView style={styles.container}>
            {/* Header fixo — fora do KeyboardAvoidingView */}
            <Header
                title={otherUserName}
                onBack={() => navigation.goBack()}
                rightElement={
                    <TouchableOpacity
                        onPress={handleViewLessons}
                        style={styles.lessonsButton}
                        accessibilityLabel="Ver aulas"
                        accessibilityRole="button"
                        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                    >
                        <BookOpen size={20} color={colors.primary[500]} />
                        <Text style={styles.lessonsButtonText}>Aulas</Text>
                    </TouchableOpacity>
                }
            />

            {/* Área que acompanha o teclado */}
            <KeyboardAvoidingView
                style={styles.keyboardView}
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
            >
                {/* Aviso de Aulas */}
                <View style={[styles.infoContainer, styles.topInfoBorder]}>
                    <BookOpen size={16} color={colors.primary[500]} />
                    <Text style={styles.infoText}>
                        Clique em "Aulas" para ver a lista completa.
                    </Text>
                </View>

                {/* Lista de mensagens */}
                <FlatList
                    ref={flatListRef}
                    data={sortedMessages}
                    renderItem={renderMessage}
                    keyExtractor={keyExtractor}
                    inverted
                    style={styles.messagesList}
                    contentContainerStyle={styles.messagesContent}
                    showsVerticalScrollIndicator={false}
                    ListEmptyComponent={
                        isLoading ? (
                            <View style={styles.loadingContainer}>
                                <LoadingState.Card />
                                <LoadingState.Card />
                            </View>
                        ) : (
                            <View style={styles.emptyContainer}>
                                <EmptyState
                                    title="Nenhuma mensagem"
                                    message="Envie uma mensagem para iniciar a conversa."
                                />
                            </View>
                        )
                    }
                />

                {/* Aviso de Localização */}
                <View style={styles.infoContainer}>
                    <MapPin size={16} color={colors.primary[500]} />
                    <Text style={styles.infoText}>
                        Clique no ícone para enviar sua localização.
                    </Text>
                </View>

                {/* Input de mensagem */}
                <ChatInput onSend={handleSend} isSending={isSending} />
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.background.light,
    },
    keyboardView: {
        flex: 1,
    },
    messagesList: {
        flex: 1,
    },
    messagesContent: {
        paddingVertical: spacing.sm,
        flexGrow: 1,
    },
    loadingContainer: {
        padding: spacing.md,
        // Invertido: conteúdo do empty fica "de cabeça para baixo" em FlatList invertida
        transform: [{ scaleY: -1 }],
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        transform: [{ scaleY: -1 }],
    },
    lessonsButton: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 4,
        paddingHorizontal: 8,
        paddingVertical: 4,
    },
    lessonsButtonText: {
        fontSize: typography.sizes.xs,
        fontFamily: typography.fontFamily.semibold,
        color: colors.primary[500],
    },
    infoContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: colors.primary[50],
        paddingHorizontal: spacing.md,
        paddingVertical: spacing.sm,
        borderTopWidth: 1,
        borderTopColor: colors.border.light,
        gap: 8,
    },
    topInfoBorder: {
        borderTopWidth: 0,
    },
    infoText: {
        fontSize: typography.sizes.xs,
        fontFamily: typography.fontFamily.medium,
        color: colors.primary[600],
    },
});
