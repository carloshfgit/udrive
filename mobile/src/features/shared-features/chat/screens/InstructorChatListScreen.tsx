import React, { useState } from 'react';
import { View, FlatList, RefreshControl, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { MessageSquare } from 'lucide-react-native';
import { Header } from '../../../../shared/components/Header';
import { Button } from '../../../../shared/components/Button';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { ChatConversationCard } from '../components/ChatConversationCard';
import { useConversations } from '../hooks/useConversations';
import { ConversationResponse } from '../api/chatApi';

export function InstructorChatListScreen() {
    const navigation = useNavigation<any>();
    const [refreshing, setRefreshing] = useState(false);

    const { data: conversations, isLoading, refetch, isError } = useConversations();


    const onRefresh = async () => {
        setRefreshing(true);
        await refetch();
        setRefreshing(false);
    };

    const handlePressConversation = (conversation: ConversationResponse) => {
        navigation.navigate('ChatRoom', {
            otherUserId: conversation.student_id,
            otherUserName: conversation.student_name
        });
    };

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <Header title="Mensagens" showBack={false} />
                <EmptyState
                    title="Ops! Algo deu errado"
                    message="Não conseguimos carregar suas mensagens."
                    action={
                        <Button
                            title="Tentar novamente"
                            onPress={onRefresh}
                            size="sm"
                        />
                    }
                />
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-neutral-50">
            <Header title="Mensagens" showBack={false} />

            <FlatList
                data={conversations}
                renderItem={({ item }) => (
                    <ChatConversationCard
                        conversation={item}
                        onPress={handlePressConversation}
                    />
                )}
                keyExtractor={(item) => item.student_id}
                contentContainerStyle={{ paddingVertical: 8, paddingBottom: 100 }}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#2563EB']} />
                }
                ListEmptyComponent={
                    isLoading ? (
                        <View className="p-4">
                            <LoadingState.Card />
                            <LoadingState.Card />
                            <LoadingState.Card />
                        </View>
                    ) : (
                        <EmptyState
                            icon={<MessageSquare size={48} color="#94A3B8" />}
                            title="Nenhuma conversa"
                            message="Suas conversas com alunos com agendamentos ativos aparecerão aqui."
                        />
                    )
                }
            />
        </SafeAreaView>
    );
}
