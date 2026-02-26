import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import {
    View,
    Text,
    FlatList,
    TextInput,
    TouchableOpacity,
    KeyboardAvoidingView,
    Platform,
    ActivityIndicator,
    Alert,
    Keyboard,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Send } from 'lucide-react-native';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Header } from '../../../../shared/components/Header';
import { useMessages } from '../hooks/useMessages';
import { MessageResponse } from '../api/chatApi';
import { wsService } from '../../../../lib/websocket';
import { useWebSocketStore } from '../../../../lib/websocketStore';
import type { WSMessage } from '../../../../lib/websocket';

// Altura estimada do Header + Banner para cálculo do offset do teclado
// Ajuste este valor se o seu Header for maior ou menor
const HEADER_OFFSET = 60 + 40; // ~60px Header + ~40px Banner

export function ChatRoomScreen() {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { otherUserId, otherUserName } = route.params;

    const [messageText, setMessageText] = useState('');
    const [isTyping, setIsTyping] = useState(false);

    // Hooks
    const { messages, sendMessage, isSending, isLoading } = useMessages(otherUserId);
    const isConnected = useWebSocketStore((s) => s.isConnected);
    const insets = useSafeAreaInsets();

    // Refs
    const typingTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Inverter mensagens para usar na FlatList inverted (UX padrão de chats)
    const reversedMessages = useMemo(() => {
        return [...messages].reverse();
    }, [messages]);

    // Listener para typing
    useEffect(() => {
        const unsubscribe = wsService.onMessage((message: WSMessage) => {
            if (
                message.type === 'typing_indicator' &&
                (message.data as Record<string, string>)?.user_id === otherUserId
            ) {
                setIsTyping(true);
                if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
                typingTimeoutRef.current = setTimeout(() => setIsTyping(false), 3000);
            }
        });

        return () => {
            unsubscribe();
            if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
        };
    }, [otherUserId]);

    const handleTextChange = useCallback(
        (text: string) => {
            setMessageText(text);
            if (isConnected && text.trim()) {
                wsService.send({ type: 'typing', receiver_id: otherUserId });
            }
        },
        [isConnected, otherUserId]
    );

    const handleSend = async () => {
        if (!messageText.trim() || isSending) return;

        const content = messageText.trim();
        setMessageText(''); // Limpa input imediatamente para UX ágil

        try {
            await sendMessage(content);
        } catch (error: any) {
            setMessageText(content); // Restaura texto em erro
            const detail = error.response?.data?.detail || 'Não foi possível enviar a mensagem.';
            Alert.alert('Erro', detail);
        }
    };

    const renderMessage = ({ item }: { item: MessageResponse }) => {
        const isMine = item.sender_id !== otherUserId;

        return (
            <View className={`mb-4 flex-row ${isMine ? 'justify-end' : 'justify-start'}`}>
                <View
                    className={`max-w-[80%] px-4 py-2 rounded-2xl ${isMine ? 'bg-blue-600 rounded-tr-none' : 'bg-neutral-100 rounded-tl-none'
                        }`}
                >
                    <Text className={`text-sm ${isMine ? 'text-white' : 'text-neutral-900'}`}>
                        {item.content}
                    </Text>
                    <Text
                        className={`text-[10px] mt-1 text-right ${isMine ? 'text-blue-100' : 'text-neutral-500'
                            }`}
                    >
                        {format(new Date(item.timestamp), 'HH:mm', { locale: ptBR })}
                    </Text>
                </View>
            </View>
        );
    };

    const renderHeaderRight = () => (
        <TouchableOpacity
            onPress={() =>
                navigation.navigate('StudentLessonHistory', {
                    studentId: otherUserId,
                    studentName: otherUserName
                })
            }
            className="bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-100 items-center justify-center mr-1"
        >
            <Text className="text-blue-600 text-[10px] font-bold uppercase tracking-wider">
                Ver Aulas
            </Text>
        </TouchableOpacity>
    );

    const TypingIndicator = () => (
        <View className="mb-4 ml-4">
            <View className="bg-neutral-100 rounded-2xl rounded-tl-none px-4 py-3 self-start">
                <View className="flex-row items-center gap-1">
                    <View className="w-1.5 h-1.5 rounded-full bg-neutral-400 animate-pulse" />
                    <View className="w-1.5 h-1.5 rounded-full bg-neutral-400 animate-pulse delay-75" />
                    <View className="w-1.5 h-1.5 rounded-full bg-neutral-400 animate-pulse delay-150" />
                </View>
            </View>
        </View>
    );

    return (
        <View className="flex-1 bg-white">
            {/* Header FORA do KeyboardAvoidingView para que fique sempre fixo no topo.
                No Android com 'resize', o view pai continua com o mesmo tamanho da janela, 
                e o KeyboardAvoidingView abaixo dele será espremido. */}
            <View style={{ paddingTop: insets.top }} className="bg-white z-10 shadow-sm">
                <Header
                    title={otherUserName}
                    onBack={() => navigation.goBack()}
                    rightElement={renderHeaderRight()}
                />

                <View className="bg-blue-50 px-4 py-2 border-b border-blue-100 flex-row items-center">
                    <Text className="text-blue-700 text-xs font-medium">
                        💡 Para ver as aulas agendadas clique em "Ver Aulas" no topo
                    </Text>
                </View>
            </View>

            <KeyboardAvoidingView
                style={{ flex: 1 }}
                behavior={Platform.OS === 'ios' ? 'padding' : undefined}
                keyboardVerticalOffset={Platform.OS === 'ios' ? HEADER_OFFSET + insets.top : 0}
            >
                <View className="flex-1">
                    {isLoading ? (
                        <View className="flex-1 justify-center items-center">
                            <ActivityIndicator color="#2563EB" size="large" />
                        </View>
                    ) : (
                        <FlatList
                            data={reversedMessages}
                            renderItem={renderMessage}
                            keyExtractor={(item) => item.id}

                            // UX: Lista invertida mantém o scroll ancorado no fundo
                            inverted
                            showsVerticalScrollIndicator={false}
                            contentContainerStyle={{
                                paddingHorizontal: 16,
                                paddingVertical: 16,
                                flexGrow: 1,
                            }}

                            // Em modo inverted, o Footer é o topo visual
                            ListFooterComponent={
                                <View className="py-6 items-center">
                                    <Text className="text-neutral-300 text-xs">
                                        Início da conversa com {otherUserName}
                                    </Text>
                                </View>
                            }

                            // Header é a parte inferior visual (acima do input)
                            ListHeaderComponent={isTyping ? <TypingIndicator /> : null}

                            // Permite fechar teclado arrastando a lista
                            keyboardDismissMode="interactive"
                            keyboardShouldPersistTaps="handled"
                        />
                    )}

                    {/* Área de Input */}
                    <View
                        className="p-4 border-t border-neutral-100 flex-row items-end bg-white"
                        style={{
                            // Garante padding extra em iPhones sem botão home quando teclado fechado
                            paddingBottom: Platform.OS === 'ios' ? Math.max(insets.bottom, 16) : 16
                        }}
                    >
                        <View className="flex-1 bg-neutral-100 rounded-3xl px-4 mr-2 border border-transparent focus:border-blue-200">
                            <TextInput
                                placeholder="Mensagem..."
                                placeholderTextColor="#A3A3A3"
                                value={messageText}
                                onChangeText={handleTextChange}
                                multiline
                                className="text-neutral-900 text-sm py-3 max-h-32 min-h-[44px]"
                                textAlignVertical="center"
                                scrollEnabled={true}
                            />
                        </View>

                        <TouchableOpacity
                            onPress={handleSend}
                            disabled={!messageText.trim() || isSending}
                            className={`w-12 h-12 rounded-full items-center justify-center shadow-sm ${!messageText.trim() || isSending ? 'bg-neutral-200' : 'bg-blue-600'
                                }`}
                            activeOpacity={0.7}
                        >
                            {isSending ? (
                                <ActivityIndicator size="small" color="#FFFFFF" />
                            ) : (
                                <Send
                                    size={20}
                                    color={!messageText.trim() ? '#A3A3A3' : '#FFFFFF'}
                                    style={{ marginLeft: 2 }}
                                />
                            )}
                        </TouchableOpacity>
                    </View>
                </View>
            </KeyboardAvoidingView>
        </View>
    );
}