/**
 * GoDrive Mobile - SelectDateTimeScreen
 *
 * Tela de seleção de data e horário para agendamento de aula.
 */

import React, { useState, useMemo } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
    ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { ChevronLeft, Star } from 'lucide-react-native';

import { Avatar } from '../../../../shared/components';
import { CalendarPicker, TimeSlotPicker } from '../components';
import { useInstructorAvailability, useAvailableTimeSlots } from '../hooks';
import { TimeSlot } from '../api/schedulingApi';

// Tipos de navegação
export type SchedulingStackParamList = {
    SelectDateTime: {
        instructorId: string;
        instructorName: string;
        instructorAvatar?: string;
        hourlyRate: number;
        licenseCategory?: string;
        rating?: number;
    };
    ConfirmBooking: {
        instructorId: string;
        instructorName: string;
        instructorAvatar?: string;
        hourlyRate: number;
        licenseCategory?: string;
        selectedDate: string; // ISO string
        selectedSlot: TimeSlot;
        durationMinutes: number;
        rating?: number;
    };
    BookingSuccess: {
        schedulingId: string;
        instructorName: string;
        scheduledDatetime: string;
        instructorId: string;
        instructorAvatar?: string;
        hourlyRate: number;
        licenseCategory?: string;
        rating?: number;
    };
};

type SelectDateTimeRouteProp = RouteProp<SchedulingStackParamList, 'SelectDateTime'>;
type SelectDateTimeNavigationProp = NativeStackNavigationProp<SchedulingStackParamList, 'SelectDateTime'>;

export function SelectDateTimeScreen() {
    const navigation = useNavigation<SelectDateTimeNavigationProp>();
    const route = useRoute<SelectDateTimeRouteProp>();
    const {
        instructorId,
        instructorName,
        instructorAvatar,
        hourlyRate,
        licenseCategory,
        rating,
    } = route.params;

    // Estado local
    const [selectedDate, setSelectedDate] = useState<Date | null>(null);
    const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
    const durationMinutes = 60; // Fixo por enquanto

    // Buscar disponibilidade semanal
    const { data: availability, isLoading: loadingAvailability } = useInstructorAvailability(instructorId);

    // Buscar horários disponíveis para a data selecionada
    const dateString = selectedDate?.toISOString().split('T')[0] || null;
    const {
        data: timeSlotsData,
        isLoading: loadingSlots,
    } = useAvailableTimeSlots(instructorId, dateString, durationMinutes);

    // Extrair dias da semana disponíveis
    const availableDaysOfWeek = useMemo(() => {
        if (!availability?.availabilities) return [];
        return [...new Set(availability.availabilities.map(a => a.day_of_week))];
    }, [availability]);

    // Handler para selecionar data
    const handleDateSelect = (date: Date) => {
        setSelectedDate(date);
        setSelectedSlot(null); // Resetar slot ao mudar data
    };

    // Handler para avançar
    const handleContinue = () => {
        if (!selectedDate || !selectedSlot) return;

        navigation.navigate('ConfirmBooking', {
            instructorId,
            instructorName,
            instructorAvatar,
            hourlyRate,
            licenseCategory,
            selectedDate: selectedDate.toISOString(),
            selectedSlot,
            durationMinutes,
            rating,
        });
    };

    const canContinue = selectedDate !== null && selectedSlot !== null;

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
                    Agendar Aula
                </Text>
                <View className="w-10" />
            </View>

            <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
                {/* Info do Instrutor */}
                <View className="px-6 py-4 flex-row items-center bg-neutral-50 border-b border-neutral-100">
                    <Avatar
                        source={instructorAvatar ? { uri: instructorAvatar } : undefined}
                        fallback={instructorName.charAt(0)}
                        size="md"
                    />
                    <View className="flex-1 ml-3">
                        <Text className="text-base font-semibold text-gray-900">
                            {instructorName}
                        </Text>
                        <View className="flex-row items-center mt-0.5">
                            {!!rating && (
                                <View className="flex-row items-center mr-2">
                                    <Star size={14} color="#F59E0B" fill="#F59E0B" />
                                    <Text className="text-sm text-gray-600 ml-1">
                                        {rating.toFixed(1)}
                                    </Text>
                                </View>
                            )}
                            {!!licenseCategory && (
                                <Text className="text-sm text-gray-500">
                                    Categoria {licenseCategory}
                                </Text>
                            )}
                        </View>
                    </View>
                    <View className="items-end">
                        <Text className="text-lg font-bold text-primary-600">
                            R$ {hourlyRate.toFixed(0)}
                        </Text>
                        <Text className="text-xs text-gray-500">/hora</Text>
                    </View>
                </View>

                {/* Calendário */}
                <View className="px-6 pt-6">
                    <Text className="text-base font-semibold text-gray-900 mb-3">
                        Selecione a data
                    </Text>
                    {loadingAvailability ? (
                        <View className="h-80 items-center justify-center">
                            <ActivityIndicator size="large" color="#2563EB" />
                        </View>
                    ) : (
                        <CalendarPicker
                            selectedDate={selectedDate}
                            onDateSelect={handleDateSelect}
                            availableDaysOfWeek={availableDaysOfWeek}
                        />
                    )}
                </View>

                {/* Horários */}
                {selectedDate && (
                    <View className="px-6 pt-6 pb-4">
                        <Text className="text-base font-semibold text-gray-900 mb-3">
                            Horários disponíveis
                        </Text>
                        <TimeSlotPicker
                            timeSlots={timeSlotsData?.time_slots || []}
                            selectedSlot={selectedSlot}
                            onSlotSelect={setSelectedSlot}
                            isLoading={loadingSlots}
                        />
                    </View>
                )}

                {/* Espaço para o botão fixo */}
                <View className="h-24" />
            </ScrollView>

            {/* Botão Fixo - Avançar */}
            <View className="absolute bottom-0 left-0 right-0 px-6 pb-8 pt-4 bg-white border-t border-gray-100">
                <TouchableOpacity
                    onPress={handleContinue}
                    disabled={!canContinue}
                    className={`py-4 rounded-xl items-center ${canContinue
                        ? 'bg-primary-600 active:bg-primary-700'
                        : 'bg-neutral-200'
                        }`}
                    accessibilityLabel="Avançar"
                >
                    <Text
                        className={`text-base font-semibold ${canContinue ? 'text-white' : 'text-neutral-400'
                            }`}
                    >
                        Avançar
                    </Text>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
