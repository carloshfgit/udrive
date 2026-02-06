import React, { useState } from 'react';
import { View, FlatList, RefreshControl, Text, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { History, Calendar } from 'lucide-react-native';
import { Header } from '../../../../shared/components/Header';
import { IconButton } from '../../../../shared/components/IconButton';
import { Button } from '../../../../shared/components/Button';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { StudentLessonCard } from '../components/StudentLessonCard';
import { useStudentSchedulings } from '../hooks/useStudentSchedulings';
import { BookingResponse } from '../api/schedulingApi';

export function MyLessonsScreen() {
    const navigation = useNavigation<any>();
    const [refreshing, setRefreshing] = useState(false);

    // Fetch only pending/confirmed lessons for the main screen
    // As per LESSONS_PLAN.md: "agendamentos ativos"
    const { data, isLoading, refetch, isError } = useStudentSchedulings();

    // Ordenar as aulas por data e hora (as mais próximas primeiro)
    const sortedSchedulings = React.useMemo(() => {
        if (!data?.schedulings) return [];

        return [...data.schedulings].sort((a, b) => {
            return new Date(a.scheduled_datetime).getTime() - new Date(b.scheduled_datetime).getTime();
        });
    }, [data?.schedulings]);

    const onRefresh = async () => {
        setRefreshing(true);
        await refetch();
        setRefreshing(false);
    };

    const handlePressDetails = (scheduling: BookingResponse) => {
        navigation.navigate('LessonDetails', { schedulingId: scheduling.id });
    };

    const renderItem = ({ item }: { item: BookingResponse }) => (
        <StudentLessonCard
            scheduling={item}
            onPressDetails={handlePressDetails}
        />
    );

    const renderHeaderRight = () => (
        <IconButton
            icon={<History size={24} color="#111318" />}
            onPress={() => navigation.navigate('History')}
            variant="ghost"
            size={44}
        />
    );

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <Header title="Minhas Aulas" showBack={false} rightElement={renderHeaderRight()} />
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
                        <View className="mb-4">
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
                        <EmptyState
                            icon={<Calendar size={32} color="#2563EB" />}
                            title="Nenhuma aula ativa"
                            message="Você ainda não possui aulas agendadas para os próximos dias."
                            action={
                                <Button
                                    title="Buscar Instrutor"
                                    onPress={() => console.log('Buscar')}
                                    size="sm"
                                />
                            }
                        />
                    )
                }
            />
        </SafeAreaView>
    );
}
