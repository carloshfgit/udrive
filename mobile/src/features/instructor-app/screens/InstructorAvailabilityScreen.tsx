/**
 * InstructorAvailabilityScreen
 *
 * Tela de configuração de disponibilidade do instrutor.
 * Permite adicionar e remover slots de horários disponíveis por dia da semana.
 */

import React, { useState, useMemo } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { ChevronLeft, Plus, Trash2, Clock } from 'lucide-react-native';

import { BottomSheet, Card, EmptyState } from '../../../shared/components';
import {
    useAvailabilities,
    useCreateAvailability,
    useDeleteAvailability,
} from '../hooks/useInstructorAvailability';
import { Availability } from '../api/scheduleApi';

// Nomes dos dias da semana
const DAY_NAMES: Record<number, string> = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo',
};

// Opções de horário para seleção
const TIME_OPTIONS = [
    '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
    '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
    '18:00', '19:00', '20:00', '21:00', '22:00',
];

// Componente de slot individual
interface AvailabilitySlotProps {
    slot: Availability;
    onDelete: (id: string) => void;
    isDeleting: boolean;
}

function AvailabilitySlot({ slot, onDelete, isDeleting }: AvailabilitySlotProps) {
    const handleDelete = () => {
        Alert.alert(
            'Remover Horário',
            `Deseja remover o horário ${slot.start_time} - ${slot.end_time}?`,
            [
                { text: 'Cancelar', style: 'cancel' },
                {
                    text: 'Remover',
                    style: 'destructive',
                    onPress: () => onDelete(slot.id),
                },
            ]
        );
    };

    return (
        <View className="flex-row items-center justify-between py-3 px-4 bg-gray-50 rounded-xl mb-2">
            <View className="flex-row items-center">
                <View className="w-10 h-10 rounded-full bg-blue-100 items-center justify-center mr-3">
                    <Clock size={20} color="#2563EB" />
                </View>
                <View>
                    <Text className="text-base font-semibold text-gray-900">
                        {slot.start_time} - {slot.end_time}
                    </Text>
                    <Text className="text-sm text-gray-500">
                        {slot.duration_minutes} minutos
                    </Text>
                </View>
            </View>
            <TouchableOpacity
                onPress={handleDelete}
                disabled={isDeleting}
                className="p-2"
                accessibilityLabel="Remover horário"
            >
                {isDeleting ? (
                    <ActivityIndicator size="small" color="#EF4444" />
                ) : (
                    <Trash2 size={20} color="#EF4444" />
                )}
            </TouchableOpacity>
        </View>
    );
}

// Componente de grupo de dia
interface DayGroupProps {
    dayOfWeek: number;
    slots: Availability[];
    onAddSlot: (day: number) => void;
    onDeleteSlot: (id: string) => void;
    deletingId: string | null;
}

function DayGroup({ dayOfWeek, slots, onAddSlot, onDeleteSlot, deletingId }: DayGroupProps) {
    return (
        <View className="mb-6">
            <View className="flex-row items-center justify-between mb-3">
                <Text className="text-base font-semibold text-gray-900">
                    {DAY_NAMES[dayOfWeek]}
                </Text>
                <TouchableOpacity
                    onPress={() => onAddSlot(dayOfWeek)}
                    className="flex-row items-center bg-blue-50 px-3 py-1.5 rounded-lg"
                >
                    <Plus size={16} color="#2563EB" />
                    <Text className="text-sm font-medium text-blue-600 ml-1">
                        Adicionar
                    </Text>
                </TouchableOpacity>
            </View>

            {slots.length > 0 ? (
                slots.map((slot) => (
                    <AvailabilitySlot
                        key={slot.id}
                        slot={slot}
                        onDelete={onDeleteSlot}
                        isDeleting={deletingId === slot.id}
                    />
                ))
            ) : (
                <View className="py-4 px-4 bg-gray-50 rounded-xl items-center">
                    <Text className="text-sm text-gray-400">
                        Nenhum horário configurado
                    </Text>
                </View>
            )}
        </View>
    );
}

// Componente de seleção de horário
interface TimePickerProps {
    label: string;
    value: string;
    onChange: (time: string) => void;
    options: string[];
}

function TimePicker({ label, value, onChange, options }: TimePickerProps) {
    return (
        <View className="mb-4">
            <Text className="text-sm font-medium text-gray-600 mb-2">{label}</Text>
            <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                className="flex-row"
                contentContainerClassName="gap-2"
            >
                {options.map((time) => {
                    const isSelected = value === time;
                    return (
                        <TouchableOpacity
                            key={time}
                            onPress={() => onChange(time)}
                            className={`
                                px-4 py-2.5 rounded-xl border-2
                                ${isSelected
                                    ? 'bg-blue-600 border-blue-600'
                                    : 'bg-white border-gray-200'
                                }
                            `}
                        >
                            <Text
                                className={`
                                    text-base font-medium
                                    ${isSelected ? 'text-white' : 'text-gray-700'}
                                `}
                            >
                                {time}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </ScrollView>
        </View>
    );
}

export function InstructorAvailabilityScreen() {
    const navigation = useNavigation();

    // Hooks de API
    const { data, isLoading, isError, refetch } = useAvailabilities();
    const createMutation = useCreateAvailability();
    const deleteMutation = useDeleteAvailability();

    // Estado do BottomSheet
    const [isSheetVisible, setIsSheetVisible] = useState(false);
    const [selectedDay, setSelectedDay] = useState<number>(0);
    const [startTime, setStartTime] = useState('08:00');
    const [endTime, setEndTime] = useState('12:00');
    const [deletingId, setDeletingId] = useState<string | null>(null);

    // Agrupar slots por dia da semana
    const slotsByDay = useMemo(() => {
        const grouped: Record<number, Availability[]> = {};
        for (let i = 0; i < 7; i++) {
            grouped[i] = [];
        }

        if (data?.availabilities) {
            data.availabilities.forEach((slot) => {
                if (grouped[slot.day_of_week]) {
                    grouped[slot.day_of_week].push(slot);
                }
            });
        }

        return grouped;
    }, [data]);

    // Abrir modal para adicionar slot
    const handleOpenAddSlot = (day: number) => {
        setSelectedDay(day);
        setStartTime('08:00');
        setEndTime('12:00');
        setIsSheetVisible(true);
    };

    // Criar novo slot
    const handleCreateSlot = async () => {
        // Validar horários
        if (startTime >= endTime) {
            Alert.alert('Erro', 'O horário de início deve ser anterior ao horário de término.');
            return;
        }

        try {
            await createMutation.mutateAsync({
                day_of_week: selectedDay,
                start_time: startTime,
                end_time: endTime,
            });
            setIsSheetVisible(false);
            Alert.alert('Sucesso', 'Horário adicionado com sucesso!');
        } catch (error: unknown) {
            console.error('[InstructorAvailabilityScreen] Create error:', error);

            // Verificar se é erro do axios com resposta da API
            let errorMessage = 'Não foi possível adicionar o horário. Tente novamente.';

            if (error && typeof error === 'object' && 'response' in error) {
                const axiosError = error as { response?: { data?: { code?: string; detail?: string } } };
                const errorCode = axiosError.response?.data?.code;
                const errorDetail = axiosError.response?.data?.detail;

                if (errorCode === 'AVAILABILITY_OVERLAP') {
                    errorMessage = 'Já existe um horário configurado que se sobrepõe a este período.';
                } else if (errorCode === 'INVALID_AVAILABILITY_TIME') {
                    errorMessage = 'O intervalo de horário é inválido.';
                } else if (errorDetail) {
                    errorMessage = errorDetail;
                }
            }

            Alert.alert('Erro', errorMessage);
        }
    };

    // Deletar slot
    const handleDeleteSlot = async (id: string) => {
        setDeletingId(id);
        try {
            await deleteMutation.mutateAsync(id);
        } catch (error: unknown) {
            console.error('[InstructorAvailabilityScreen] Delete error:', error);
            Alert.alert('Erro', 'Não foi possível remover o horário. Tente novamente.');
        } finally {
            setDeletingId(null);
        }
    };

    // Estados de carregamento e erro
    if (isLoading) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
                    <TouchableOpacity
                        onPress={() => navigation.goBack()}
                        className="w-10 h-10 items-center justify-center"
                    >
                        <ChevronLeft size={24} color="#111318" />
                    </TouchableOpacity>
                    <Text className="flex-1 text-lg font-bold text-gray-900 text-center">
                        Meus Horários
                    </Text>
                    <View className="w-10" />
                </View>
                <View className="flex-1 items-center justify-center">
                    <ActivityIndicator size="large" color="#2563EB" />
                    <Text className="text-gray-500 mt-4">Carregando horários...</Text>
                </View>
            </SafeAreaView>
        );
    }

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
                    <TouchableOpacity
                        onPress={() => navigation.goBack()}
                        className="w-10 h-10 items-center justify-center"
                    >
                        <ChevronLeft size={24} color="#111318" />
                    </TouchableOpacity>
                    <Text className="flex-1 text-lg font-bold text-gray-900 text-center">
                        Meus Horários
                    </Text>
                    <View className="w-10" />
                </View>
                <EmptyState
                    title="Erro ao carregar"
                    message="Não foi possível carregar seus horários."
                    action={
                        <TouchableOpacity
                            onPress={() => refetch()}
                            className="bg-blue-600 px-6 py-3 rounded-xl"
                        >
                            <Text className="text-white font-semibold">Tentar novamente</Text>
                        </TouchableOpacity>
                    }
                />
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
                <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    className="w-10 h-10 items-center justify-center"
                    accessibilityLabel="Voltar"
                >
                    <ChevronLeft size={24} color="#111318" />
                </TouchableOpacity>
                <Text className="flex-1 text-lg font-bold text-gray-900 text-center">
                    Meus Horários
                </Text>
                <View className="w-10" />
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerClassName="py-6"
                showsVerticalScrollIndicator={false}
            >
                {/* Descrição */}
                <View className="bg-blue-50 p-4 rounded-xl mb-6">
                    <Text className="text-blue-800 font-medium">
                        💡 Configure sua disponibilidade
                    </Text>
                    <Text className="text-blue-700 text-sm mt-1">
                        Defina os horários em que você está disponível para dar aulas. Alunos poderão agendar apenas nos horários configurados.
                    </Text>
                </View>

                {/* Lista por dia */}
                {[0, 1, 2, 3, 4, 5, 6].map((day) => (
                    <DayGroup
                        key={day}
                        dayOfWeek={day}
                        slots={slotsByDay[day]}
                        onAddSlot={handleOpenAddSlot}
                        onDeleteSlot={handleDeleteSlot}
                        deletingId={deletingId}
                    />
                ))}
            </ScrollView>

            {/* BottomSheet para adicionar horário */}
            <BottomSheet
                isVisible={isSheetVisible}
                onClose={() => setIsSheetVisible(false)}
                title={`Adicionar Horário - ${DAY_NAMES[selectedDay]}`}
            >
                <View className="pb-4">
                    {/* Seleção de horário inicial */}
                    <TimePicker
                        label="Horário de Início"
                        value={startTime}
                        onChange={setStartTime}
                        options={TIME_OPTIONS}
                    />

                    {/* Seleção de horário final */}
                    <TimePicker
                        label="Horário de Término"
                        value={endTime}
                        onChange={setEndTime}
                        options={TIME_OPTIONS.filter((t) => t > startTime)}
                    />

                    {/* Botão de adicionar */}
                    <TouchableOpacity
                        onPress={handleCreateSlot}
                        disabled={createMutation.isPending}
                        className={`
                            py-4 rounded-xl items-center justify-center mt-4
                            ${createMutation.isPending ? 'bg-blue-400' : 'bg-blue-600 active:bg-blue-700'}
                        `}
                    >
                        {createMutation.isPending ? (
                            <ActivityIndicator size="small" color="#ffffff" />
                        ) : (
                            <Text className="text-base font-semibold text-white">
                                Adicionar Horário
                            </Text>
                        )}
                    </TouchableOpacity>
                </View>
            </BottomSheet>
        </SafeAreaView>
    );
}
