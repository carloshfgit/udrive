import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    FlatList,
    TextInput,
    TouchableOpacity,
    KeyboardAvoidingView,
    Platform,
    SafeAreaView,
    ActivityIndicator,
    Alert,
    Keyboard
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

export function ChatRoomScreen() {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { otherUserId, otherUserName } = route.params;

    const [messageText, setMessageText] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const { messages, sendMessage, isSending, isLoading } = useMessages(otherUserId);
    const isConnected = useWebSocketStore((s) => s.isConnected);
    const insets = useSafeAreaInsets();
    const flatListRef = useRef<FlatList>(null);
    const typingTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Rola a lista quando o teclado aparecer
    useEffect(() => {
        const keyboardDidShowListener = Keyboard.addListener(
            'keyboardDidShow',
            () => {
                setTimeout(() => {
                    flatListRef.current?.scrollToEnd({ animated: true });
                }, 100);
            }
        );

        return () => {
            keyboardDidShowListener.remove();
        };
    }, []);

    // Listener para indicador de typing do outro usuário
    useEffect(() => {
        const unsubscribe = wsService.onMessage((message: WSMessage) => {
            if (
                message.type === 'typing_indicator' &&
                (message.data as Record<string, string>)?.user_id === otherUserId
            ) {
                setIsTyping(true);

                // Limpar indicador após 3 segundos
                if (typingTimeoutRef.current) {
                    clearTimeout(typingTimeoutRef.current);
                }
                typingTimeoutRef.current = setTimeout(() => {
                    setIsTyping(false);
                }, 3000);
            }
        });

        return () => {
            unsubscribe();
            if (typingTimeoutRef.current) {
                clearTimeout(typingTimeoutRef.current);
            }
        };
    }, [otherUserId]);

    // Enviar indicador de typing ao digitar
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
        setMessageText('');

        try {
            await sendMessage(content);
        } catch (error: any) {
            setMessageText(content); // Devolve o texto em caso de erro
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
            onPress={() => navigation.navigate('StudentLessonHistory', { studentId: otherUserId, studentName: otherUserName })}
            className="bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-100 items-center justify-center mr-1"
        >
            <Text className="text-blue-600 text-[10px] font-bold uppercase tracking-wider">Ver Aulas</Text>
        </TouchableOpacity>
    );

    return (
        <SafeAreaView className="flex-1 bg-white">
            <Header
                title={otherUserName}
                onBack={() => navigation.goBack()}
                rightElement={renderHeaderRight()}
            />

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : undefined}
                className="flex-1"
                keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
            >
                {/* Dica para ver aulas */}
                <View className="bg-blue-50 px-4 py-2 border-b border-blue-100 flex-row items-center">
                    <Text className="text-blue-700 text-xs font-medium">
                        💡 Para ver as aulas agendadas clique em "Ver Aulas" no topo
                    </Text>
                </View>

                <View className="flex-1 px-4">
                    {isLoading ? (
                        <View className="flex-1 justify-center items-center">
                            <ActivityIndicator color="#2563EB" />
                        </View>
                    ) : (
                        <FlatList
                            ref={flatListRef}
                            data={messages}
                            renderItem={renderMessage}
                            keyExtractor={(item) => item.id}
                            showsVerticalScrollIndicator={false}
                            contentContainerStyle={{ paddingVertical: 16 }}
                            onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                            ListEmptyComponent={
                                <View className="flex-1 justify-center items-center py-20">
                                    <Text className="text-neutral-400 text-center">
                                        Nenhuma mensagem ainda.{"\n"}Os agendamentos confirmados permitem a comunicação direta.
                                    </Text>
                                </View>
                            }
                        />
                    )}

                    {/* Indicador de "digitando..." */}
                    {isTyping && (
                        <View className="px-2 pb-1">
                            <Text className="text-xs text-neutral-400 italic">
                                {otherUserName} está digitando...
                            </Text>
                        </View>
                    )}
                </View>

                {/* Input Area */}
                <View
                    className="p-4 border-t border-neutral-100 flex-row items-center bg-white"
                    style={{ paddingBottom: Platform.OS === 'ios' ? Math.max(insets.bottom, 16) : 16 }}
                >
                    <View className="flex-1 bg-neutral-100 rounded-full px-4 py-2 mr-2 max-h-32">
                        <TextInput
                            placeholder="Mensagem..."
                            value={messageText}
                            onChangeText={handleTextChange}
                            multiline
                            className="text-neutral-900 text-sm py-1"
                            blurOnSubmit={false}
                        />
                    </View>

                    <TouchableOpacity
                        onPress={handleSend}
                        disabled={!messageText.trim() || isSending}
                        className={`w-10 h-10 rounded-full items-center justify-center ${!messageText.trim() || isSending ? 'bg-neutral-200' : 'bg-blue-600'
                            }`}
                    >
                        {isSending ? (
                            <ActivityIndicator size="small" color="#FFFFFF" />
                        ) : (
                            <Send size={20} color="#FFFFFF" />
                        )}
                    </TouchableOpacity>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
