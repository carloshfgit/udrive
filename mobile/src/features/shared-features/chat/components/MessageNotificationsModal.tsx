import React from 'react';
import {
    View,
    Text,
    Modal,
    TouchableOpacity,
    FlatList,
    SafeAreaView,
    ActivityIndicator,
} from 'react-native';
import { X, MessageSquare } from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';
import { Avatar } from '../../../../shared/components/Avatar';
import { useStudentConversations } from '../hooks/useStudentConversations';
import { StudentConversationResponse } from '../api/chatApi';

interface MessageNotificationsModalProps {
    visible: boolean;
    onClose: () => void;
}

export function MessageNotificationsModal({ visible, onClose }: MessageNotificationsModalProps) {
    const navigation = useNavigation<any>();
    const { data: conversations, isLoading } = useStudentConversations();

    const conversationsWithMessages = (conversations ?? []).filter(
        (c) => c.unread_count > 0 || c.last_message
    );

    const handlePress = (conversation: StudentConversationResponse) => {
        onClose();
        navigation.navigate('ChatRoom', {
            otherUserId: conversation.instructor_id,
            otherUserName: conversation.instructor_name,
        });
    };

    const renderItem = ({ item }: { item: StudentConversationResponse }) => (
        <TouchableOpacity
            onPress={() => handlePress(item)}
            className="flex-row items-center p-4 border-b border-neutral-100 active:bg-neutral-50"
        >
            <Avatar fallback={item.instructor_name} size="sm" />
            <View className="flex-1 ml-3">
                <Text className="text-neutral-900 font-bold text-sm" numberOfLines={1}>
                    {item.instructor_name}
                </Text>
                <Text className="text-neutral-500 text-xs mt-0.5" numberOfLines={1}>
                    {item.unread_count > 0
                        ? `te mandou ${item.unread_count === 1 ? 'uma mensagem' : `${item.unread_count} mensagens`}, clique aqui para ver`
                        : item.last_message?.content ?? 'Nenhuma mensagem ainda'}
                </Text>
            </View>
            {item.unread_count > 0 && (
                <View className="bg-red-500 rounded-full h-5 min-w-[20px] px-1.5 items-center justify-center ml-2">
                    <Text className="text-white text-[10px] font-bold">
                        {item.unread_count}
                    </Text>
                </View>
            )}
        </TouchableOpacity>
    );

    return (
        <Modal
            visible={visible}
            animationType="slide"
            transparent
            onRequestClose={onClose}
        >
            <View className="flex-1 justify-end bg-black/40">
                <View className="bg-white rounded-t-3xl max-h-[60%] min-h-[200px]">
                    {/* Header */}
                    <View className="flex-row items-center justify-between px-5 pt-5 pb-3 border-b border-neutral-100">
                        <View className="flex-row items-center">
                            <MessageSquare size={20} color="#2563EB" />
                            <Text className="text-neutral-900 font-bold text-lg ml-2">Mensagens</Text>
                        </View>
                        <TouchableOpacity onPress={onClose} className="p-1">
                            <X size={22} color="#6B7280" />
                        </TouchableOpacity>
                    </View>

                    {/* Content */}
                    {isLoading ? (
                        <View className="py-10 items-center">
                            <ActivityIndicator color="#2563EB" />
                        </View>
                    ) : (
                        <FlatList
                            data={conversationsWithMessages}
                            renderItem={renderItem}
                            keyExtractor={(item) => item.instructor_id}
                            ListEmptyComponent={
                                <View className="py-10 items-center px-6">
                                    <MessageSquare size={40} color="#CBD5E1" />
                                    <Text className="text-neutral-400 text-center mt-3 text-sm">
                                        Nenhuma mensagem no momento.
                                    </Text>
                                </View>
                            }
                        />
                    )}
                </View>
            </View>
        </Modal>
    );
}
