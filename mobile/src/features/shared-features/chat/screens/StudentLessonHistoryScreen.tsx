import React from 'react';
import { View, FlatList, Text, SafeAreaView } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { Header } from '../../../../shared/components/Header';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { StudentLessonCard } from '../../scheduling/components/StudentLessonCard';
import { useStudentLessons } from '../hooks/useStudentLessons';

export function StudentLessonHistoryScreen() {
    const route = useRoute<any>();
    const { studentId, studentName } = route.params;

    const { data: lessons, isLoading, isError } = useStudentLessons(studentId);

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <Header title={`Aulas - ${studentName}`} />
                <EmptyState
                    title="Ops! Algo deu errado"
                    message="Não conseguimos carregar o histórico de aulas."
                />
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-white">
            <Header title={`Aulas - ${studentName}`} />

            <FlatList
                data={lessons}
                renderItem={({ item }) => (
                    <StudentLessonCard
                        scheduling={item}
                        onPressDetails={() => { }} // Desativado nesta vista simplificada por enquanto
                    />
                )}
                keyExtractor={(item) => item.id}
                contentContainerStyle={{ padding: 16 }}
                ListEmptyComponent={
                    isLoading ? (
                        <View>
                            <LoadingState.Card />
                            <LoadingState.Card />
                        </View>
                    ) : (
                        <EmptyState
                            title="Nenhuma aula encontrada"
                            message="Não existem registros de aulas entre você e este aluno."
                        />
                    )
                }
                ListHeaderComponent={
                    lessons && lessons.length > 0 ? (
                        <View className="mb-4">
                            <Text className="text-neutral-500 text-sm font-medium">
                                Todas as aulas (passadas e futuras)
                            </Text>
                        </View>
                    ) : null
                }
            />
        </SafeAreaView>
    );
}
