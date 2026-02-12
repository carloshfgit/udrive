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
    Check,
    CheckCircle,
    User,
    XCircle,
    MessageSquare,
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
import { Scheduling, SchedulingStatus } from '../api/scheduleApi';
import { useAuth } from '../../auth/hooks/useAuth';
import type { InstructorScheduleStackParamList } from '../navigation/InstructorScheduleStack';

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

// Componente de Card de Aula
interface ScheduleCardProps {
    scheduling: Scheduling;
    onConfirm: (id: string) => void;
    onComplete: (id: string) => void;
    onCancel: (id: string) => void;
    onReschedule: (scheduling: Scheduling) => void;
    isConfirming: boolean;
    isCompleting: boolean;
    isCancelling: boolean;
}

function ScheduleCard({
    scheduling,
    onConfirm,
    onComplete,
    onCancel,
    onReschedule,
    isConfirming,
    isCompleting,
    isCancelling,
}: ScheduleCardProps) {
    const scheduledTime = new Date(scheduling.scheduled_datetime);
    const timeStr = scheduledTime.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
    });

    const getStatusColor = (status: SchedulingStatus) => {
        switch (status) {
            case 'pending':
                return { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200', accent: 'bg-yellow-500', label: 'Pendente' };
            case 'confirmed':
                return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', accent: 'bg-emerald-500', label: 'Confirmado' };
            case 'completed':
                return { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', accent: 'bg-blue-500', label: 'Concluído' };
            case 'cancelled':
                return { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', accent: 'bg-red-500', label: 'Cancelado' };
            case 'reschedule_requested':
                return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', accent: 'bg-amber-500', label: 'Reagendamento' };
            default:
                return { bg: 'bg-gray-50', text: 'text-gray-700', border: 'border-gray-200', accent: 'bg-gray-500', label: status };
        }
    };

    const statusInfo = getStatusColor(scheduling.status);

    const handleConfirm = () => {
        Alert.alert(
            'Confirmar Aula',
            `Deseja confirmar a aula das ${timeStr}?`,
            [
                { text: 'Cancelar', style: 'cancel' },
                { text: 'Confirmar', onPress: () => onConfirm(scheduling.id) },
            ]
        );
    };

    const handleComplete = () => {
        Alert.alert(
            'Concluir Aula',
            `Deseja marcar a aula das ${timeStr} como concluída?`,
            [
                { text: 'Voltar', style: 'cancel' },
                { text: 'Concluir', onPress: () => onComplete(scheduling.id) },
            ]
        );
    };

    const handleCancel = () => {
        Alert.alert(
            'Cancelar Aula',
            `Deseja realmente cancelar a aula das ${timeStr}?\n\nEsta ação não pode ser desfeita.`,
            [
                { text: 'Voltar', style: 'cancel' },
                {
                    text: 'Cancelar Aula',
                    style: 'destructive',
                    onPress: () => onCancel(scheduling.id),
                },
            ]
        );
    };
    const navigation = useNavigation<any>();
    const { user } = useAuth();
    const isSelfRequested = scheduling.rescheduled_by === user?.id;

    return (
        <Card variant="outlined" className="mb-4 overflow-hidden border-gray-100">
            <View className="flex-row">
                {/* Indicador lateral de status */}
                <View className={`w-1.5 ${statusInfo.accent}`} />

                <View className="flex-1 p-4">
                    {/* Linha Superior: Horário e Status */}
                    <View className="flex-row items-center justify-between mb-4">
                        <View>
                            <Text className="text-3xl font-black text-gray-900 tracking-tighter">
                                {timeStr}
                            </Text>
                            <View className="flex-row items-center mt-0.5">
                                <Clock size={12} color="#9CA3AF" />
                                <Text className="text-xs text-gray-400 font-medium ml-1">
                                    {scheduling.duration_minutes} min de aula
                                </Text>
                            </View>
                        </View>

                        <View className={`px-3 py-1.5 rounded-full border ${statusInfo.bg} ${statusInfo.border}`}>
                            <Text className={`text-[10px] uppercase font-bold tracking-wider ${statusInfo.text}`}>
                                {statusInfo.label}
                            </Text>
                        </View>
                    </View>

                    {/* Bloco do Aluno */}
                    <View className="flex-row items-center bg-gray-50 border border-gray-100 p-3 rounded-2xl mb-4">
                        <View className="w-12 h-12 rounded-full bg-white border border-gray-100 items-center justify-center mr-3 shadow-sm">
                            <User size={24} color="#2563EB" />
                        </View>
                        <View className="flex-1">
                            <Text className="text-[10px] text-gray-400 font-bold uppercase tracking-tight">Aluno</Text>
                            <Text className="text-base font-bold text-gray-900 leading-tight">
                                {scheduling.student_name || 'Aluno'}
                            </Text>
                        </View>
                        <TouchableOpacity
                            onPress={() => navigation.navigate('InstructorChat', {
                                screen: 'ChatRoom',
                                params: {
                                    otherUserId: scheduling.student_id,
                                    otherUserName: scheduling.student_name || 'Aluno'
                                }
                            })}
                            className="bg-white p-2.5 rounded-xl border border-gray-100 shadow-sm active:bg-gray-50"
                        >
                            <MessageSquare size={18} color="#2563EB" />
                        </TouchableOpacity>
                    </View>

                    {/* Detalhes Adicionais */}
                    <View className="flex-row items-center justify-between pb-3 border-b border-gray-50 mb-4">
                        <View className="flex-row items-center">
                            <View className="w-2 h-2 rounded-full bg-blue-500 mr-2" />
                            <Text className="text-sm text-gray-500">Valor da aula</Text>
                        </View>
                        <Text className="text-lg font-black text-gray-900">
                            R$ {Number(scheduling.price).toFixed(2)}
                        </Text>
                    </View>

                    {/* Ações */}
                    {scheduling.status === 'reschedule_requested' && (
                        <TouchableOpacity
                            onPress={() => navigation.navigate('RescheduleDetails', { scheduling })}
                            className="flex-row items-center justify-center py-3.5 rounded-2xl bg-amber-500 active:bg-amber-600 shadow-sm"
                        >
                            <Clock size={18} color="#ffffff" />
                            <Text className="text-white font-bold ml-2">
                                {isSelfRequested ? 'Minha Sugestão' : 'Ver Solicitação'}
                            </Text>
                        </TouchableOpacity>
                    )}

                    {scheduling.status === 'pending' && (
                        <TouchableOpacity
                            onPress={handleConfirm}
                            disabled={isConfirming}
                            className={`
                                flex-row items-center justify-center py-3.5 rounded-2xl
                                ${isConfirming ? 'bg-blue-400' : 'bg-blue-600 active:bg-blue-700 shadow-sm shadow-blue-200'}
                            `}
                        >
                            {isConfirming ? (
                                <ActivityIndicator size="small" color="#ffffff" />
                            ) : (
                                <>
                                    <Check size={18} color="#ffffff" />
                                    <Text className="text-white font-bold ml-2">
                                        Confirmar Aula
                                    </Text>
                                </>
                            )}
                        </TouchableOpacity>
                    )}

                    {scheduling.status === 'confirmed' && (
                        <TouchableOpacity
                            onPress={handleComplete}
                            disabled={isCompleting}
                            className={`
                                flex-row items-center justify-center py-3.5 rounded-2xl
                                ${isCompleting ? 'bg-emerald-400' : 'bg-emerald-600 active:bg-emerald-700 shadow-sm shadow-emerald-200'}
                            `}
                        >
                            {isCompleting ? (
                                <ActivityIndicator size="small" color="#ffffff" />
                            ) : (
                                <>
                                    <CheckCircle size={18} color="#ffffff" />
                                    <Text className="text-white font-bold ml-2">
                                        Marcar como Concluída
                                    </Text>
                                </>
                            )}
                        </TouchableOpacity>
                    )}

                    {/* Botão de Reagendar - para pending e confirmed */}
                    {(scheduling.status === 'pending' || scheduling.status === 'confirmed') && (
                        <TouchableOpacity
                            onPress={() => onReschedule(scheduling)}
                            className="flex-row items-center justify-center py-3 rounded-2xl mt-2 bg-white active:bg-gray-50 border border-gray-100"
                        >
                            <Clock size={18} color="#6B7280" />
                            <Text className="text-gray-600 font-semibold ml-2">
                                Reagendar
                            </Text>
                        </TouchableOpacity>
                    )}
                </View>
            </View>
        </Card>
    );
}

export function InstructorScheduleScreen() {
    const navigation = useNavigation<NavigationProp>();
    const route = useRoute<RouteProp<InstructorScheduleStackParamList, 'InstructorScheduleMain'>>();
    const queryClient = useQueryClient();

    // Estado do calendário
    const today = new Date();
    const [currentMonth, setCurrentMonth] = useState(today.getMonth());
    const [currentYear, setCurrentYear] = useState(today.getFullYear());
    const [selectedDate, setSelectedDate] = useState(today);

    // Atualizar data selecionada se vier via parâmetro
    React.useEffect(() => {
        if (route.params?.initialDate) {
            const date = new Date(route.params.initialDate);
            if (!isNaN(date.getTime())) {
                setSelectedDate(date);
                setCurrentMonth(date.getMonth());
                setCurrentYear(date.getFullYear());
            }
        }
    }, [route.params?.initialDate]);

    // Estado de mutações em andamento
    const [confirmingId, setConfirmingId] = useState<string | null>(null);
    const [completingId, setCompletingId] = useState<string | null>(null);
    const [cancellingId, setCancellingId] = useState<string | null>(null);

    // Formatar data selecionada para API
    const formattedDate = formatDateForAPI(selectedDate);

    // Hooks de API
    const { data, isLoading, isError, refetch, isRefetching } = useScheduleByDate(formattedDate);
    const confirmMutation = useConfirmScheduling();
    const completeMutation = useCompleteScheduling();
    const cancelMutation = useCancelScheduling();
    const rescheduleMutation = useRequestReschedule();

    // Estado do modal de reagendamento
    const [rescheduleModalVisible, setRescheduleModalVisible] = useState(false);
    const [schedulingToReschedule, setSchedulingToReschedule] = useState<Scheduling | null>(null);

    // Atualizar ao ganhar foco
    useFocusEffect(
        React.useCallback(() => {
            refetch();
        }, [refetch])
    );

    const onRefresh = React.useCallback(async () => {
        // Invalidar tudo relacionado à agenda do instrutor para garantir que pontos no calendário atualizem
        await queryClient.invalidateQueries({ queryKey: INSTRUCTOR_SCHEDULE_QUERY_KEY });
    }, [queryClient]);

    // Buscar datas com agendamentos para o mês atual (mês é 1-indexed na API)
    const { data: schedulingDatesData } = useSchedulingDates(currentYear, currentMonth + 1);

    // Set para lookup rápido de datas com agendamentos
    const schedulingDates = useMemo(() => {
        if (!schedulingDatesData?.dates) return new Set<string>();
        return new Set(schedulingDatesData.dates);
    }, [schedulingDatesData]);

    // Verificar se uma data tem agendamentos
    const hasSchedulings = (date: Date) => {
        const dateStr = formatDateForAPI(date);
        return schedulingDates.has(dateStr);
    };

    // Gerar dias do mês atual
    const daysInMonth = useMemo(
        () => getDaysInMonth(currentYear, currentMonth),
        [currentYear, currentMonth]
    );

    // Mês anterior
    const handlePrevMonth = () => {
        if (currentMonth === 0) {
            setCurrentMonth(11);
            setCurrentYear(currentYear - 1);
        } else {
            setCurrentMonth(currentMonth - 1);
        }
    };

    // Próximo mês
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
    };

    // Confirmar aula
    const handleConfirm = async (id: string) => {
        setConfirmingId(id);
        try {
            await confirmMutation.mutateAsync(id);
            Alert.alert('Sucesso', 'Aula confirmada!');
        } catch (error: any) {
            console.error('[InstructorScheduleScreen] Confirm error:', error);
            const message = error?.response?.data?.detail || 'Não foi possível confirmar a aula.';
            Alert.alert('Erro', message);
        } finally {
            setConfirmingId(null);
        }
    };

    // Completar aula
    const handleComplete = async (id: string) => {
        setCompletingId(id);
        try {
            await completeMutation.mutateAsync(id);
            Alert.alert('Sucesso', 'Aula marcada como concluída!');
        } catch (error: any) {
            console.error('[InstructorScheduleScreen] Complete error:', error);
            const detail = error?.response?.data?.detail;
            const message = typeof detail === 'string' && detail.includes('solicite ao aluno')
                ? detail
                : (detail || 'Não foi possível concluir a aula.');
            Alert.alert('Atenção', message);
        } finally {
            setCompletingId(null);
        }
    };

    // Reagendar aula
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
            Alert.alert('Sucesso', 'Solicitação de reagendamento enviada!');
            setRescheduleModalVisible(false);
            setSchedulingToReschedule(null);
        } catch (error: any) {
            console.error('[InstructorScheduleScreen] Reschedule error:', error);
            const message = error?.response?.data?.detail || 'Não foi possível solicitar o reagendamento.';
            Alert.alert('Erro', message);
        }
    };

    // Verificar se é o dia selecionado
    const isSelectedDay = (date: Date) => {
        return (
            date.getDate() === selectedDate.getDate() &&
            date.getMonth() === selectedDate.getMonth() &&
            date.getFullYear() === selectedDate.getFullYear()
        );
    };

    // Verificar se é hoje
    const isToday = (date: Date) => {
        return (
            date.getDate() === today.getDate() &&
            date.getMonth() === today.getMonth() &&
            date.getFullYear() === today.getFullYear()
        );
    };

    // Verificar se é do mês atual
    const isCurrentMonth = (date: Date) => {
        return date.getMonth() === currentMonth;
    };

    // Formatar data selecionada para exibição
    const selectedDateStr = selectedDate.toLocaleDateString('pt-BR', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
    });

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
                                onConfirm={handleConfirm}
                                onComplete={handleComplete}
                                onCancel={() => { }} // Not used but kept for interface compatibility
                                onReschedule={handleReschedulePress}
                                isConfirming={confirmingId === scheduling.id}
                                isCompleting={completingId === scheduling.id}
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

                {/* Dica */}
                <View className="mx-4 mt-6 bg-blue-50 p-4 rounded-xl">
                    <Text className="text-blue-800 font-medium">
                        💡 Dicas
                    </Text>
                    <Text className="text-blue-700 text-sm mt-1">
                        {[
                            '- Configure seus horários disponíveis tocando em "Horários" para que alunos possam agendar aulas com você.',
                            '- Fique atento aos seus agendamentos e confirme-os para que os alunos possam realizar as aulas.',
                            '- Observe as datas no calendário, aquelas com um ponto verde são dias com aulas agendadas.',
                        ].join('\n')}
                    </Text>
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
