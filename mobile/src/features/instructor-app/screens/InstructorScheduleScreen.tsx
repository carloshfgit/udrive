/**
 * InstructorScheduleScreen
 *
 * Tela de agenda do instrutor com calendário visual e lista de aulas.
 */

import React, { useState, useMemo } from 'react';
import {
    View,
    Text,
    SafeAreaView,
    ScrollView,
    TouchableOpacity,
    ActivityIndicator,
    Alert,
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
} from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

import { Card, EmptyState } from '../../../shared/components';
import {
    useScheduleByDate,
    useConfirmScheduling,
    useCompleteScheduling,
    useCancelScheduling,
    useSchedulingDates,
} from '../hooks/useInstructorSchedule';
import { Scheduling, SchedulingStatus } from '../api/scheduleApi';
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
    isConfirming: boolean;
    isCompleting: boolean;
    isCancelling: boolean;
}

function ScheduleCard({
    scheduling,
    onConfirm,
    onComplete,
    onCancel,
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
                return { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pendente' };
            case 'confirmed':
                return { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Confirmado' };
            case 'completed':
                return { bg: 'bg-secondary-100', text: 'text-secondary-800', label: 'Concluído' };
            case 'cancelled':
                return { bg: 'bg-red-100', text: 'text-red-800', label: 'Cancelado' };
            case 'reschedule_requested':
                return { bg: 'bg-amber-100', text: 'text-amber-800', label: 'Reagendamento' };
            default:
                return { bg: 'bg-gray-100', text: 'text-gray-800', label: status };
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

    return (
        <Card variant="outlined" className="mb-3">
            <View className="p-4">
                {/* Header do Card */}
                <View className="flex-row items-center justify-between mb-3">
                    <View className="flex-row items-center">
                        <View className="w-10 h-10 rounded-full bg-blue-100 items-center justify-center mr-3">
                            <User size={20} color="#2563EB" />
                        </View>
                        <View>
                            <Text className="text-base font-semibold text-gray-900">
                                {scheduling.student_name || 'Aluno'}
                            </Text>
                            <View className="flex-row items-center mt-0.5">
                                <Clock size={14} color="#6B7280" />
                                <Text className="text-sm text-gray-500 ml-1">
                                    {timeStr} - {scheduling.duration_minutes}min
                                </Text>
                            </View>
                        </View>
                    </View>

                    {/* Badge de Status */}
                    <View className={`px-2.5 py-1 rounded-full ${statusInfo.bg}`}>
                        <Text className={`text-xs font-medium ${statusInfo.text}`}>
                            {statusInfo.label}
                        </Text>
                    </View>
                </View>

                {/* Valor */}
                <View className="flex-row items-center justify-between py-2 border-t border-gray-100">
                    <Text className="text-sm text-gray-500">Valor da aula</Text>
                    <Text className="text-base font-semibold text-gray-900">
                        R$ {Number(scheduling.price).toFixed(2)}
                    </Text>
                </View>

                {/* Ações */}
                {scheduling.status === 'reschedule_requested' && (
                    <TouchableOpacity
                        onPress={() => navigation.navigate('RescheduleDetails', { scheduling })}
                        className="flex-row items-center justify-center py-3 rounded-xl mt-2 bg-amber-500 active:bg-amber-600 shadow-sm"
                    >
                        <Clock size={18} color="#ffffff" />
                        <Text className="text-white font-semibold ml-2">
                            Ver Solicitação
                        </Text>
                    </TouchableOpacity>
                )}

                {scheduling.status === 'pending' && (
                    <TouchableOpacity
                        onPress={handleConfirm}
                        disabled={isConfirming}
                        className={`
                            flex-row items-center justify-center py-3 rounded-xl mt-2
                            ${isConfirming ? 'bg-blue-400' : 'bg-blue-600 active:bg-blue-700'}
                        `}
                    >
                        {isConfirming ? (
                            <ActivityIndicator size="small" color="#ffffff" />
                        ) : (
                            <>
                                <Check size={18} color="#ffffff" />
                                <Text className="text-white font-semibold ml-2">
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
                            flex-row items-center justify-center py-3 rounded-xl mt-2
                            ${isCompleting ? 'bg-green-400' : 'bg-green-600 active:bg-green-700'}
                        `}
                    >
                        {isCompleting ? (
                            <ActivityIndicator size="small" color="#ffffff" />
                        ) : (
                            <>
                                <CheckCircle size={18} color="#ffffff" />
                                <Text className="text-white font-semibold ml-2">
                                    Marcar como Concluída
                                </Text>
                            </>
                        )}
                    </TouchableOpacity>
                )}

                {/* Botão de Cancelar - para pending e confirmed */}
                {(scheduling.status === 'pending' || scheduling.status === 'confirmed') && (
                    <TouchableOpacity
                        onPress={handleCancel}
                        disabled={isCancelling}
                        className={`
                            flex-row items-center justify-center py-3 rounded-xl mt-2
                            border-2 border-red-500
                            ${isCancelling ? 'bg-red-100' : 'bg-white active:bg-red-50'}
                        `}
                    >
                        {isCancelling ? (
                            <ActivityIndicator size="small" color="#ef4444" />
                        ) : (
                            <>
                                <XCircle size={18} color="#ef4444" />
                                <Text className="text-red-500 font-semibold ml-2">
                                    Cancelar Aula
                                </Text>
                            </>
                        )}
                    </TouchableOpacity>
                )}
            </View>
        </Card>
    );
}

export function InstructorScheduleScreen() {
    const navigation = useNavigation<NavigationProp>();

    // Estado do calendário
    const today = new Date();
    const [currentMonth, setCurrentMonth] = useState(today.getMonth());
    const [currentYear, setCurrentYear] = useState(today.getFullYear());
    const [selectedDate, setSelectedDate] = useState(today);

    // Estado de mutações em andamento
    const [confirmingId, setConfirmingId] = useState<string | null>(null);
    const [completingId, setCompletingId] = useState<string | null>(null);
    const [cancellingId, setCancellingId] = useState<string | null>(null);

    // Formatar data selecionada para API
    const formattedDate = formatDateForAPI(selectedDate);

    // Hooks de API
    const { data, isLoading, isError, refetch } = useScheduleByDate(formattedDate);
    const confirmMutation = useConfirmScheduling();
    const completeMutation = useCompleteScheduling();
    const cancelMutation = useCancelScheduling();

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
            const message = error?.response?.data?.detail || 'Não foi possível concluir a aula.';
            Alert.alert('Erro', message);
        } finally {
            setCompletingId(null);
        }
    };

    // Cancelar aula
    const handleCancel = async (id: string) => {
        setCancellingId(id);
        try {
            await cancelMutation.mutateAsync({ schedulingId: id });
            Alert.alert('Sucesso', 'Aula cancelada!');
        } catch (error: any) {
            console.error('[InstructorScheduleScreen] Cancel error:', error);
            const message = error?.response?.data?.detail || 'Não foi possível cancelar a aula.';
            Alert.alert('Erro', message);
        } finally {
            setCancellingId(null);
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
                                onCancel={handleCancel}
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
                        💡 Dica
                    </Text>
                    <Text className="text-blue-700 text-sm mt-1">
                        Configure seus horários disponíveis tocando em "Horários" para que alunos possam agendar aulas com você.
                    </Text>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
