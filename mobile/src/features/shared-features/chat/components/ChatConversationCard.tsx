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
    const hasUnread = conversation.unread_count > 0;

    const formattedTime = lastMessage
        ? format(new Date(lastMessage.timestamp), 'HH:mm', { locale: ptBR })
        : '';

    const nextLessonDate = conversation.next_lesson_at
        ? format(new Date(conversation.next_lesson_at), "dd 'de' MMMM", { locale: ptBR })
        : 'Sem aulas próximas';

    return (
        <TouchableOpacity
            onPress={() => onPress(conversation)}
            className={`mx-4 my-2 p-4 rounded-2xl shadow-sm active:bg-neutral-50 ${hasUnread
                    ? 'bg-blue-50 border-2 border-blue-500'
                    : 'bg-white border border-neutral-100'
                }`}
            style={{
                shadowColor: hasUnread ? '#2563EB' : '#000',
                shadowOffset: { width: 0, height: 2 },
                shadowOpacity: hasUnread ? 0.15 : 0.05,
                shadowRadius: 8,
                elevation: hasUnread ? 4 : 2
            }}
        >
            <View className="flex-row items-center">
                {/* Avatar with unread indicator */}
                <View className="relative">
                    <Avatar
                        fallback={conversation.student_name}
                        size="md"
                    />
                    {hasUnread && (
                        <View
                            className="absolute -top-1 -right-1 bg-blue-600 rounded-full border-2 border-white"
                            style={{ width: 16, height: 16 }}
                        />
                    )}
                </View>

                <View className="flex-1 ml-4">
                    <View className="flex-row justify-between items-center mb-1">
                        <Text className="text-neutral-900 font-bold text-base" numberOfLines={1}>
                            {conversation.student_name}
                        </Text>
                        {lastMessage && (
                            <Text className={`text-xs ${hasUnread ? 'text-blue-700 font-semibold' : 'text-neutral-500'}`}>
                                {formattedTime}
                            </Text>
                        )}
                    </View>

                    <View className="flex-row justify-between items-center mb-2">
                        <Text
                            className={`text-sm flex-1 mr-2 ${hasUnread ? 'text-neutral-900 font-semibold' : 'text-neutral-500'}`}
                            numberOfLines={1}
                        >
                            {lastMessage ? lastMessage.content : 'Nenhuma mensagem ainda'}
                        </Text>

                        {hasUnread && (
                            <View className="bg-blue-600 rounded-full h-6 min-w-[24px] px-2 items-center justify-center">
                                <Text className="text-white text-xs font-bold">
                                    {conversation.unread_count}
                                </Text>
                            </View>
                        )}
                    </View>

                    {/* Next Lesson Info */}
                    <View className="flex-row items-center pt-2 border-t border-neutral-100">
                        <View className={`px-2 py-1 rounded-md flex-row items-center ${hasUnread ? 'bg-blue-100' : 'bg-blue-50'
                            }`}>
                            <Text className={`text-[10px] font-medium uppercase tracking-wider ${hasUnread ? 'text-blue-800' : 'text-blue-700'
                                }`}>
                                Próxima aula: <Text className="font-bold">{nextLessonDate}</Text>
                            </Text>
                        </View>
                    </View>
                </View>
            </View>
        </TouchableOpacity>
    );
}
