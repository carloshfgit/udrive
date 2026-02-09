import React, { useState, useRef, useEffect } from 'react';
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
    Alert
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Send } from 'lucide-react-native';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Header } from '../../../../shared/components/Header';
import { useMessages } from '../hooks/useMessages';
import { MessageResponse } from '../api/chatApi';

export function ChatRoomScreen() {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { otherUserId, otherUserName } = route.params;

    const [messageText, setMessageText] = useState('');
    const { messages, sendMessage, isSending, isLoading } = useMessages(otherUserId);
    const insets = useSafeAreaInsets();
    const flatListRef = useRef<FlatList>(null);

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
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                className="flex-1"
                keyboardVerticalOffset={Platform.OS === 'ios' ? 60 : 0}
            >
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
                            inverted
                            showsVerticalScrollIndicator={false}
                            contentContainerStyle={{ paddingVertical: 16 }}
                            ListEmptyComponent={
                                <View className="flex-1 justify-center items-center py-20">
                                    <Text className="text-neutral-400 text-center">
                                        Nenhuma mensagem ainda.{"\n"}Os agendamentos confirmados permitem a comunicação direta.
                                    </Text>
                                </View>
                            }
                        />
                    )}
                </View>

                {/* Input Area */}
                <View
                    className="p-4 border-t border-neutral-100 flex-row items-center bg-white"
                    style={{ paddingBottom: Math.max(insets.bottom, 16) }}
                >
                    <View className="flex-1 bg-neutral-100 rounded-full px-4 py-2 mr-2 max-h-32">
                        <TextInput
                            placeholder="Mensagem..."
                            value={messageText}
                            onChangeText={setMessageText}
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
