/**
 * InstructorScheduleScreen
 *
 * Tela de agenda do instrutor com calendário visual e lista de aulas.
 */

import React, { useState, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
    View,
    Text,
    SafeAreaView,
    ScrollView,
    TouchableOpacity,
    ActivityIndicator,
    Alert,
    RefreshControl,
} from 'react-native';
import {
    ChevronLeft,
    ChevronRight,
    Clock,
    Plus,
} from 'lucide-react-native';
import { useNavigation, useFocusEffect, useRoute, RouteProp } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { Card, EmptyState } from '../../../shared/components';
import {
    useScheduleByDate,
    useConfirmScheduling,
    useCompleteScheduling,
    useCancelScheduling,
    useRequestReschedule,
    useSchedulingDates,
    INSTRUCTOR_SCHEDULE_QUERY_KEY,
} from '../hooks/useInstructorSchedule';
import { RescheduleModal } from '../../student-app/scheduling/components/RescheduleModal';
import { Scheduling } from '../api/scheduleApi';
import { useAuth } from '../../auth/hooks/useAuth';
import type { InstructorScheduleStackParamList } from '../navigation/InstructorScheduleStack';
import { ScheduleCard } from '../components/ScheduleCard';

type NavigationProp = NativeStackNavigationProp<InstructorScheduleStackParamList>;

// Nomes dos dias da semana (abreviados)
const DAY_NAMES = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
const MONTH_NAMES = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
];

// Utilitário para formatar data para API
function formatDateForAPI(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Utilitário para gerar dias do mês
function getDaysInMonth(year: number, month: number): Date[] {
    const days: Date[] = [];
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    // Adicionar dias vazios do início (para alinhar com dia da semana)
    const startDay = firstDay.getDay();
    for (let i = 0; i < startDay; i++) {
        const prevDate = new Date(year, month, -(startDay - i - 1));
        days.push(prevDate);
    }

    // Dias do mês atual
    for (let d = 1; d <= lastDay.getDate(); d++) {
        days.push(new Date(year, month, d));
    }

    return days;
}

export default function InstructorScheduleScreen() {
    const navigation = useNavigation<NavigationProp>();
    const route = useRoute<RouteProp<InstructorScheduleStackParamList, 'InstructorScheduleMain'>>();
    const { user } = useAuth();
    const queryClient = useQueryClient();

    const today = new Date();
    const [currentMonth, setCurrentMonth] = useState(today.getMonth());
    const [currentYear, setCurrentYear] = useState(today.getFullYear());
    const [selectedDate, setSelectedDate] = useState(today);
    const [completingId, setCompletingId] = useState<string | null>(null);
    const [cancellingId, setCancellingId] = useState<string | null>(null);
    const [rescheduleModalVisible, setRescheduleModalVisible] = useState(false);
    const [schedulingToReschedule, setSchedulingToReschedule] = useState<Scheduling | null>(null);

    // Fetch agendamentos por data
    const {
        data,
        isLoading,
        isError,
        refetch,
        isRefetching,
    } = useScheduleByDate(formatDateForAPI(selectedDate));

    // Fetch das datas com agendamentos (para exibir os indicadores no calendário)
    const {
        data: schedulingDates,
        isLoading: isDatesLoading,
        refetch: refetchDates,
    } = useSchedulingDates(currentYear, currentMonth + 1);

    // Mutations
    const completeMutation = useCompleteScheduling();
    const cancelMutation = useCancelScheduling();
    const rescheduleMutation = useRequestReschedule();

    // Calcular os dias do mês
    const daysInMonth = useMemo(
        () => getDaysInMonth(currentYear, currentMonth),
        [currentYear, currentMonth]
    );

    // Verifica se uma data é hoje
    const isToday = (date: Date) => {
        return (
            date.getDate() === today.getDate() &&
            date.getMonth() === today.getMonth() &&
            date.getFullYear() === today.getFullYear()
        );
    };

    // Verifica se uma data está selecionada
    const isSelectedDay = (date: Date) => {
        return (
            date.getDate() === selectedDate.getDate() &&
            date.getMonth() === selectedDate.getMonth() &&
            date.getFullYear() === selectedDate.getFullYear()
        );
    };

    // Verifica se uma data pertence ao mês atual (navegando no calendário)
    const isCurrentMonth = (date: Date) => {
        return date.getMonth() === currentMonth;
    };

    // Verifica se a data tem agendamentos
    const hasSchedulings = (date: Date) => {
        if (!schedulingDates?.dates) return false;
        const dateStr = formatDateForAPI(date);
        return schedulingDates.dates.includes(dateStr);
    };

    // Navegação de mês
    const handlePrevMonth = () => {
        if (currentMonth === 0) {
            setCurrentMonth(11);
            setCurrentYear(currentYear - 1);
        } else {
            setCurrentMonth(currentMonth - 1);
        }
    };

    const handleNextMonth = () => {
        if (currentMonth === 11) {
            setCurrentMonth(0);
            setCurrentYear(currentYear + 1);
        } else {
            setCurrentMonth(currentMonth + 1);
        }
    };

    // Selecionar data
    const handleSelectDate = (date: Date) => {
        setSelectedDate(date);
        // Se clicar em uma data de outro mês, ajustar o calendário
        if (date.getMonth() !== currentMonth) {
            setCurrentMonth(date.getMonth());
            setCurrentYear(date.getFullYear());
        }
    };

    // Formatar data selecionada para exibição
    const selectedDateStr = useMemo(() => {
        const options: Intl.DateTimeFormatOptions = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        };
        return selectedDate.toLocaleDateString('pt-BR', options);
    }, [selectedDate]);

    // Handlers para ações nos cards

    const handleComplete = async (id: string) => {
        setCompletingId(id);
        try {
            await completeMutation.mutateAsync(id);
            queryClient.invalidateQueries({ queryKey: [INSTRUCTOR_SCHEDULE_QUERY_KEY] });
            refetchDates();
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Não foi possível concluir a aula.';
            Alert.alert('Erro', errorMessage);
        } finally {
            setCompletingId(null);
        }
    };

    const handleCancel = async (id: string) => {
        setCancellingId(id);
        try {
            await cancelMutation.mutateAsync({ schedulingId: id });
            queryClient.invalidateQueries({ queryKey: [INSTRUCTOR_SCHEDULE_QUERY_KEY] });
            refetchDates();
        } catch (error: any) {
            const errorMessage = error.response?.data?.detail || error.message || 'Não foi possível cancelar a aula.';
            Alert.alert('Erro', errorMessage);
        } finally {
            setCancellingId(null);
        }
    };

    const handleReschedulePress = (scheduling: Scheduling) => {
        setSchedulingToReschedule(scheduling);
        setRescheduleModalVisible(true);
    };

    const handleConfirmReschedule = async (newDatetime: string) => {
        if (!schedulingToReschedule) return;

        try {
            await rescheduleMutation.mutateAsync({
                schedulingId: schedulingToReschedule.id,
                newDatetime,
            });
            setRescheduleModalVisible(false);
            setSchedulingToReschedule(null);
            queryClient.invalidateQueries({ queryKey: [INSTRUCTOR_SCHEDULE_QUERY_KEY] });
            refetchDates();
            Alert.alert('Sucesso', 'Reagendamento solicitado com sucesso!');
        } catch (error: any) {
            Alert.alert('Erro', error.message || 'Não foi possível solicitar reagendamento.');
        }
    };

    // Atualizar ao focar na tela
    useFocusEffect(
        React.useCallback(() => {
            refetch();
            refetchDates();
        }, [refetch, refetchDates])
    );

    // Se vier de uma notificação, navegar para a data
    React.useEffect(() => {
        if (route.params?.initialDate) {
            let targetDate: Date;
            if (route.params.initialDate.includes('-') && route.params.initialDate.length === 10) {
                // Ensure YYYY-MM-DD is parsed as local time to prevent timezone offset bugs
                const [year, month, day] = route.params.initialDate.split('-');
                targetDate = new Date(Number(year), Number(month) - 1, Number(day));
            } else {
                targetDate = new Date(route.params.initialDate);
            }
            setSelectedDate(targetDate);
            setCurrentMonth(targetDate.getMonth());
            setCurrentYear(targetDate.getFullYear());

            // Clear the param so it can trigger again if the user navigates with the same date
            navigation.setParams({ initialDate: undefined });
        }
    }, [route.params?.initialDate, navigation]);

    const onRefresh = React.useCallback(() => {
        refetch();
        refetchDates();
    }, [refetch, refetchDates]);

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="px-4 py-4 flex-row items-center justify-between border-b border-gray-100">
                <Text className="text-xl font-bold text-gray-900">
                    Minha Agenda
                </Text>
                <TouchableOpacity
                    onPress={() => navigation.navigate('InstructorAvailability')}
                    className="bg-blue-600 px-4 py-2 rounded-lg flex-row items-center"
                    accessibilityLabel="Definir disponibilidade"
                >
                    <Plus size={18} color="#ffffff" />
                    <Text className="text-white font-semibold ml-1">
                        Horários
                    </Text>
                </TouchableOpacity>
            </View>

            <ScrollView
                className="flex-1"
                contentContainerClassName="pb-8"
                showsVerticalScrollIndicator={false}
                refreshControl={
                    <RefreshControl
                        refreshing={isRefetching}
                        onRefresh={onRefresh}
                        colors={['#2563EB']}
                        tintColor="#2563EB"
                    />
                }
            >
                {/* Navegação do Calendário */}
                <View className="flex-row items-center justify-between px-4 py-3">
                    <TouchableOpacity
                        onPress={handlePrevMonth}
                        className="p-2"
                        accessibilityLabel="Mês anterior"
                    >
                        <ChevronLeft size={24} color="#111318" />
                    </TouchableOpacity>
                    <Text className="text-lg font-semibold text-gray-900">
                        {MONTH_NAMES[currentMonth]} {currentYear}
                    </Text>
                    <TouchableOpacity
                        onPress={handleNextMonth}
                        className="p-2"
                        accessibilityLabel="Próximo mês"
                    >
                        <ChevronRight size={24} color="#111318" />
                    </TouchableOpacity>
                </View>

                {/* Cabeçalho dos dias da semana */}
                <View className="flex-row px-2 mb-2">
                    {DAY_NAMES.map((day) => (
                        <View key={day} className="flex-1 items-center py-2">
                            <Text className="text-xs font-medium text-gray-500 uppercase">
                                {day}
                            </Text>
                        </View>
                    ))}
                </View>

                {/* Grid do Calendário */}
                <View className="flex-row flex-wrap px-2 mb-4">
                    {daysInMonth.map((date, index) => {
                        const selected = isSelectedDay(date);
                        const todayDay = isToday(date);
                        const current = isCurrentMonth(date);

                        return (
                            <TouchableOpacity
                                key={index}
                                onPress={() => handleSelectDate(date)}
                                className="w-[14.28%] aspect-square items-center justify-center"
                            >
                                <View
                                    className={`
                                        w-10 h-10 rounded-full items-center justify-center
                                        ${selected ? 'bg-blue-600' : ''}
                                        ${todayDay && !selected ? 'border-2 border-blue-600' : ''}
                                    `}
                                >
                                    <Text
                                        className={`
                                            text-sm font-medium
                                            ${selected ? 'text-white' : ''}
                                            ${!current && !selected ? 'text-gray-300' : ''}
                                            ${current && !selected ? 'text-gray-900' : ''}
                                        `}
                                    >
                                        {date.getDate()}
                                    </Text>
                                    {/* Indicador de agendamentos */}
                                    {hasSchedulings(date) && !selected && (
                                        <View className="absolute bottom-0.5 w-1.5 h-1.5 rounded-full bg-green-500" />
                                    )}
                                </View>
                            </TouchableOpacity>
                        );
                    })}
                </View>

                {/* Dica */}
                <View className="mx-4 mb-6 bg-blue-50 p-4 rounded-xl">
                    <Text className="text-blue-800 font-medium">
                        💡 Dicas
                    </Text>
                    <Text className="text-blue-700 text-sm mt-1">
                        {[
                            '- Configure seus horários disponíveis tocando em "Horários" para que alunos possam agendar aulas com você.',
                            '- Observe as datas no calendário, aquelas com um ponto verde são dias com aulas agendadas.',
                        ].join('\n')}
                    </Text>
                </View>

                {/* Título da data selecionada */}
                <View className="px-4 mb-4">
                    <Text className="text-lg font-semibold text-gray-900 capitalize">
                        {selectedDateStr}
                    </Text>
                </View>

                {/* Lista de Aulas do Dia */}
                <View className="px-4">
                    {isLoading ? (
                        <View className="items-center py-12">
                            <ActivityIndicator size="large" color="#2563EB" />
                            <Text className="text-gray-500 mt-4">Carregando aulas...</Text>
                        </View>
                    ) : isError ? (
                        <EmptyState
                            title="Erro ao carregar"
                            message="Não foi possível carregar as aulas do dia."
                            action={
                                <TouchableOpacity
                                    onPress={() => refetch()}
                                    className="bg-blue-600 px-6 py-3 rounded-xl"
                                >
                                    <Text className="text-white font-semibold">Tentar novamente</Text>
                                </TouchableOpacity>
                            }
                        />
                    ) : data?.schedulings && data.schedulings.length > 0 ? (
                        data.schedulings.map((scheduling) => (
                            <ScheduleCard
                                key={scheduling.id}
                                scheduling={scheduling}
                                onCancel={() => { }} // Not used but kept for interface compatibility
                                onReschedule={handleReschedulePress}
                                isCancelling={cancellingId === scheduling.id}
                            />
                        ))
                    ) : (
                        <Card variant="outlined">
                            <View className="p-6 items-center">
                                <View className="w-16 h-16 rounded-full bg-gray-100 items-center justify-center mb-4">
                                    <Clock size={32} color="#9CA3AF" />
                                </View>
                                <Text className="text-base font-medium text-gray-900 text-center">
                                    Nenhuma aula agendada
                                </Text>
                                <Text className="text-sm text-gray-500 text-center mt-1">
                                    Você não tem aulas marcadas para este dia.
                                </Text>
                            </View>
                        </Card>
                    )}
                </View>
            </ScrollView>

            <RescheduleModal
                isVisible={rescheduleModalVisible}
                onClose={() => setRescheduleModalVisible(false)}
                onConfirm={handleConfirmReschedule}
                instructorId={schedulingToReschedule?.instructor_id || ''}
                durationMinutes={schedulingToReschedule?.duration_minutes || 50}
                isSubmitting={rescheduleMutation.isPending}
            />
        </SafeAreaView>
    );
}