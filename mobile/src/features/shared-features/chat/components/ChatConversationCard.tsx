import React from 'react';
import { TouchableOpacity, View, Text } from 'react-native';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Avatar } from '../../../../shared/components/Avatar';
import { ConversationResponse } from '../api/chatApi';

interface ChatConversationCardProps {
    conversation: ConversationResponse;
    onPress: (conversation: ConversationResponse) => void;
}

export function ChatConversationCard({ conversation, onPress }: ChatConversationCardProps) {
    const lastMessage = conversation.last_message;

    const formattedTime = lastMessage
        ? format(new Date(lastMessage.timestamp), 'HH:mm', { locale: ptBR })
        : '';

    const nextLessonDate = conversation.next_lesson_at
        ? format(new Date(conversation.next_lesson_at), "dd 'de' MMMM", { locale: ptBR })
        : 'Sem aulas próximas';

    return (
        <TouchableOpacity
            onPress={() => onPress(conversation)}
            className="mx-4 my-2 p-4 bg-white rounded-2xl border border-neutral-100 shadow-sm active:bg-neutral-50"
            style={{
                shadowColor: '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: 0.05,
                shadowRadius: 8,
                elevation: 2
            }}
        >
            <View className="flex-row items-center">
                <Avatar
                    fallback={conversation.student_name}
                    size="md"
                />

                <View className="flex-1 ml-4">
                    <View className="flex-row justify-between items-center mb-1">
                        <Text className="text-neutral-900 font-bold text-base" numberOfLines={1}>
                            {conversation.student_name}
                        </Text>
                        {lastMessage && (
                            <Text className="text-neutral-500 text-xs">
                                {formattedTime}
                            </Text>
                        )}
                    </View>

                    <View className="flex-row justify-between items-center mb-2">
                        <Text
                            className={`text-sm flex-1 mr-2 ${conversation.unread_count > 0 ? 'text-neutral-900 font-medium' : 'text-neutral-500'}`}
                            numberOfLines={1}
                        >
                            {lastMessage ? lastMessage.content : 'Nenhuma mensagem ainda'}
                        </Text>

                        {conversation.unread_count > 0 && (
                            <View className="bg-blue-600 rounded-full h-5 min-w-[20px] px-1.5 items-center justify-center">
                                <Text className="text-white text-[10px] font-bold">
                                    {conversation.unread_count}
                                </Text>
                            </View>
                        )}
                    </View>

                    {/* Next Lesson Info */}
                    <View className="flex-row items-center pt-2 border-t border-neutral-50">
                        <View className="bg-blue-50 px-2 py-1 rounded-md flex-row items-center">
                            <Text className="text-[10px] text-blue-700 font-medium uppercase tracking-wider">
                                Próxima aula: <Text className="font-bold">{nextLessonDate}</Text>
                            </Text>
                        </View>
                    </View>
                </View>
            </View>
        </TouchableOpacity>
    );
}
