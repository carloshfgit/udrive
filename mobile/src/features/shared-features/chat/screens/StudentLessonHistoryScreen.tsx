import React from 'react';
import { View, FlatList, Text, SafeAreaView } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useAuthStore } from '@lib/store';
import { Header } from '../../../../shared/components/Header';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { StudentLessonCard } from '../../scheduling/components/StudentLessonCard';
import { useLessonHistory } from '../hooks/useLessonHistory';

export function StudentLessonHistoryScreen() {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { user } = useAuthStore();

    // Para instrutor: recebe studentId e studentName
    // Para aluno: recebe instructorId e instructorName (mas com nomes studentId/studentName por compatibilidade)
    const { studentId, studentName } = route.params;

    const isInstructor = user?.user_type === 'instructor';
    const { data: lessons, isLoading, isError } = useLessonHistory(studentId);

    const displayName = studentName || (isInstructor ? 'Aluno' : 'Instrutor');
    const title = `Aulas - ${displayName}`;

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <Header title={title} onBack={() => navigation.goBack()} />
                <EmptyState
                    title="Ops! Algo deu errado"
                    message="Não conseguimos carregar o histórico de aulas."
                />
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-white">
            <Header title={title} onBack={() => navigation.goBack()} />

            <FlatList
                data={lessons}
                renderItem={({ item }) => (
                    <StudentLessonCard
                        scheduling={item}
                        variant={isInstructor ? 'instructor' : 'student'}
                        onPressDetails={() => {
                            if (isInstructor) {
                                // Instrutor: navega para a agenda do instrutor
                                navigation.navigate('InstructorSchedule', {
                                    screen: 'InstructorScheduleMain',
                                    params: { initialDate: item.scheduled_datetime }
                                });
                            } else {
                                // Aluno: navega para os detalhes da aula
                                navigation.navigate('LessonDetails', {
                                    schedulingId: item.id
                                });
                            }
                        }}
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
                            message={
                                isInstructor
                                    ? "Não existem registros de aulas entre você e este aluno."
                                    : "Não existem registros de aulas entre você e este instrutor."
                            }
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

