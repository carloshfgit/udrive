import React, { useState, useCallback } from 'react';
import { View, FlatList, RefreshControl, Text, SafeAreaView } from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { History, Calendar, MessageSquare, ShoppingCart, Info } from 'lucide-react-native';
import { Header } from '../../../../shared/components/Header';
import { IconButton } from '../../../../shared/components/IconButton';
import { Button } from '../../../../shared/components/Button';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { StudentLessonCard } from '../components/StudentLessonCard';
import { useStudentSchedulings } from '../hooks/useStudentSchedulings';
import { useCartItems } from '../hooks/usePayment';
import { BookingResponse } from '../api/schedulingApi';
import { useUnreadCount } from '../../chat/hooks/useUnreadCount';
import { MessageNotificationsModal } from '../../chat/components/MessageNotificationsModal';

export function MyLessonsScreen() {
    const navigation = useNavigation<any>();
    const [refreshing, setRefreshing] = useState(false);
    const [isMessagesModalVisible, setIsMessagesModalVisible] = useState(false);

    // Fetch only pending/confirmed lessons for the main screen
    const { data, isLoading, refetch, isError } = useStudentSchedulings();
    const { data: cartData, refetch: refetchCart } = useCartItems();
    const { unreadCount, refetch: refetchUnread } = useUnreadCount();

    const cartCount = cartData?.schedulings?.length ?? 0;

    const onRefresh = useCallback(async () => {
        setRefreshing(true);
        await Promise.all([
            refetch(),
            refetchCart(),
            refetchUnread()
        ]);
        setRefreshing(false);
    }, [refetch, refetchCart, refetchUnread]);

    // Atualizar dados ao focar na tela
    useFocusEffect(
        useCallback(() => {
            onRefresh();
        }, [onRefresh])
    );

    // Refresh ao clicar no item da tab bar (mesmo se já estiver na tela)
    React.useEffect(() => {
        const unsubscribe = navigation.addListener('tabPress', () => {
            onRefresh();
        });

        return unsubscribe;
    }, [navigation, onRefresh]);

    // Os dados já vêm ordenados (ASC) do backend para esta tela
    const sortedSchedulings = React.useMemo(() => {
        return (data?.schedulings ?? []).filter(
            (s) => s.status.toLowerCase() !== 'completed' && s.payment_status === 'completed'
        );
    }, [data?.schedulings]);

    const handlePressDetails = (scheduling: BookingResponse) => {
        navigation.navigate('LessonDetails', { schedulingId: scheduling.id });
    };

    const renderItem = ({ item }: { item: BookingResponse }) => (
        <StudentLessonCard
            scheduling={item}
            onPressDetails={handlePressDetails}
        />
    );

    const renderHeaderLeft = () => (
        <View className="relative">
            <IconButton
                icon={<MessageSquare size={24} color="#111318" />}
                onPress={() => setIsMessagesModalVisible(true)}
                variant="ghost"
                size={44}
            />
            {unreadCount > 0 && (
                <View className="absolute -top-0.5 -right-0.5 bg-red-500 rounded-full h-3 w-3 border-2 border-white" />
            )}
        </View>
    );

    const renderHeaderRight = () => (
        <View className="flex-row items-center">
            <View className="relative mr-1">
                <IconButton
                    icon={<ShoppingCart size={24} color="#111318" />}
                    onPress={() => navigation.navigate('Cart')}
                    variant="ghost"
                    size={44}
                />
                {cartCount > 0 && (
                    <View className="absolute -top-0.5 -right-0.5 bg-red-500 rounded-full h-5 w-5 items-center justify-center border-2 border-white">
                        <Text className="text-white text-[10px] font-bold">{cartCount}</Text>
                    </View>
                )}
            </View>
        </View>
    );

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <Header title="Minhas Aulas" showBack={false} leftElement={renderHeaderLeft()} rightElement={renderHeaderRight()} />
                <EmptyState
                    title="Ops! Algo deu errado"
                    message="Não conseguimos carregar suas aulas no momento."
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
        <SafeAreaView className="flex-1 bg-white">
            <Header
                title="Minhas Aulas"
                showBack={false}
                leftElement={renderHeaderLeft()}
                rightElement={renderHeaderRight()}
            />

            <FlatList
                data={sortedSchedulings}
                renderItem={renderItem}
                keyExtractor={(item) => item.id}
                contentContainerStyle={{ padding: 16, paddingBottom: 80 }}
                showsVerticalScrollIndicator={false}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#2563EB']} />
                }
                ListHeaderComponent={
                    sortedSchedulings.length > 0 ? (
                        <View className="mb-6">
                            <View className="flex-row items-center bg-blue-50 p-4 rounded-2xl border border-blue-100 mb-6">
                                <View className="bg-blue-100 p-2 rounded-full mr-3">
                                    <Info size={20} color="#2563EB" />
                                </View>
                                <Text className="flex-1 text-blue-900 text-sm leading-5">
                                    Clique em <Text className="font-bold">"Ver Detalhes"</Text> para gerenciar sua aula e enviar mensagens ao instrutor.
                                </Text>
                            </View>

                            <Text className="text-neutral-500 text-sm font-medium">
                                Próximas aulas agendadas
                            </Text>
                        </View>
                    ) : null
                }
                ListEmptyComponent={
                    isLoading ? (
                        <View>
                            <LoadingState.Card />
                            <LoadingState.Card />
                            <LoadingState.Card />
                        </View>
                    ) : (
                        cartCount > 0 ? (
                            <EmptyState
                                icon={<ShoppingCart size={32} color="#EF4444" />}
                                title="Carrinho com itens"
                                message="Você ainda não tem aulas confirmadas.
                                Suas aulas serão confirmadas e aparecerão aqui após o pagamento."
                                action={
                                    <View className="w-full gap-3">
                                        <Button
                                            title={`Ver Carrinho (${cartCount} ${cartCount === 1 ? 'item' : 'itens'})`}
                                            onPress={() => navigation.navigate('Cart')}
                                            size="sm"
                                        />
                                    </View>
                                }
                            />
                        ) : (
                            <EmptyState
                                icon={<Calendar size={32} color="#2563EB" />}
                                title="Nenhuma aula ativa"
                                message="Você ainda não possui aulas agendadas para os próximos dias."
                                action={
                                    <Button
                                        title="Buscar Instrutor"
                                        onPress={() => navigation.navigate('Search')}
                                        size="sm"
                                    />
                                }
                            />
                        )
                    )
                }
            />

            <MessageNotificationsModal
                visible={isMessagesModalVisible}
                onClose={() => setIsMessagesModalVisible(false)}
            />
        </SafeAreaView>
    );
}

