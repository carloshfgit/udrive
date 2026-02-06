import React, { useState } from 'react';
import { View, FlatList, RefreshControl, Text, SafeAreaView } from 'react-native';
import { History, Calendar } from 'lucide-react-native';
import { Header } from '../../../../shared/components/Header';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { StudentLessonCard } from '../../../shared-features/scheduling/components/StudentLessonCard';
import { useStudentHistory } from '../../../shared-features/scheduling/hooks/useStudentHistory';
import { BookingResponse } from '../../../shared-features/scheduling/api/schedulingApi';
import { LessonEvaluationModal } from '../components/LessonEvaluationModal';

export function HistoryScreen() {
    const [refreshing, setRefreshing] = useState(false);
    const [selectedLesson, setSelectedLesson] = useState<BookingResponse | null>(null);
    const [modalVisible, setModalVisible] = useState(false);

    // Fetch completed/cancelled lessons
    const { data, isLoading, refetch, isError } = useStudentHistory();

    const sortedSchedulings = React.useMemo(() => {
        if (!data?.schedulings) return [];

        return [...data.schedulings].sort((a, b) => {
            return new Date(b.scheduled_datetime).getTime() - new Date(a.scheduled_datetime).getTime();
        });
    }, [data?.schedulings]);

    const onRefresh = async () => {
        setRefreshing(true);
        await refetch();
        setRefreshing(false);
    };

    const handlePressDetails = (scheduling: BookingResponse) => {
        console.log('Ver detalhes:', scheduling.id);
        // Próxima fase: navegar para Detalhes
    };

    const handlePressEvaluate = (scheduling: BookingResponse) => {
        setSelectedLesson(scheduling);
        setModalVisible(true);
    };

    const renderItem = ({ item }: { item: BookingResponse }) => (
        <StudentLessonCard
            scheduling={item}
            onPressDetails={handlePressDetails}
            onPressEvaluate={handlePressEvaluate}
        />
    );

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <Header title="Histórico" />
                <EmptyState
                    title="Ops! Algo deu errado"
                    message="Não conseguimos carregar seu histórico no momento."
                />
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-white">
            <Header title="Histórico" />

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
                                Aulas anteriores e canceladas
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
                            icon={<History size={32} color="#2563EB" />}
                            title="Nenhum histórico"
                            message="Você ainda não possui aulas concluídas ou canceladas."
                        />
                    )
                }
            />

            <LessonEvaluationModal
                visible={modalVisible}
                onClose={() => setModalVisible(false)}
                scheduling={selectedLesson}
                onSuccess={() => refetch()}
            />
        </SafeAreaView>
    );
}
