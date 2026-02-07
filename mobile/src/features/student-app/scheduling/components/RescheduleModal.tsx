/**
 * GoDrive Mobile - RescheduleModal Component
 *
 * Modal para seleção de nova data e horário para reagendamento.
 * Utiliza CalendarPicker e TimeSlotPicker existentes.
 */

import React, { useState, useMemo } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { BottomSheet } from '../../../../shared/components/BottomSheet';
import { Button } from '../../../../shared/components/Button';
import { CalendarPicker, TimeSlotPicker } from '../../../shared-features/scheduling/components';
import { useInstructorAvailability, useAvailableTimeSlots } from '../../../shared-features/scheduling/hooks';
import { TimeSlot } from '../../../shared-features/scheduling/api/schedulingApi';

interface RescheduleModalProps {
    isVisible: boolean;
    onClose: () => void;
    onConfirm: (newDatetime: string) => void;
    instructorId: string;
    durationMinutes: number;
    isSubmitting?: boolean;
}

export function RescheduleModal({
    isVisible,
    onClose,
    onConfirm,
    instructorId,
    durationMinutes,
    isSubmitting = false,
}: RescheduleModalProps) {
    const [selectedDate, setSelectedDate] = useState<Date | null>(null);
    const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);

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

    const handleDateSelect = (date: Date) => {
        setSelectedDate(date);
        setSelectedSlot(null);
    };

    const handleConfirm = () => {
        if (!selectedDate || !selectedSlot) return;

        // Montar datetime final
        const finalDate = new Date(selectedDate);
        const [hours, minutes] = selectedSlot.start_time.split(':').map(Number);
        finalDate.setHours(hours, minutes, 0, 0);

        onConfirm(finalDate.toISOString());
    };

    const canConfirm = selectedDate !== null && selectedSlot !== null && !isSubmitting;

    return (
        <BottomSheet
            isVisible={isVisible}
            onClose={onClose}
            title="Sugerir Novo Horário"
        >
            <View className="pb-8">
                <Text className="text-neutral-500 text-sm mb-6">
                    Selecione uma nova data e horário. O instrutor precisará aprovar esta solicitação.
                </Text>

                {/* Calendário */}
                <View className="mb-6">
                    <Text className="text-base font-bold text-neutral-900 mb-3">
                        Data
                    </Text>
                    {loadingAvailability ? (
                        <View className="h-40 items-center justify-center">
                            <ActivityIndicator size="small" color="#2563EB" />
                        </View>
                    ) : (
                        <CalendarPicker
                            selectedDate={selectedDate}
                            onDateSelect={handleDateSelect}
                            availableDaysOfWeek={availableDaysOfWeek}
                            minDate={new Date(Date.now() + 86400000)} // Começar de amanhã
                        />
                    )}
                </View>

                {/* Horários */}
                {selectedDate && (
                    <View className="mb-8">
                        <Text className="text-base font-bold text-neutral-900 mb-3">
                            Horário
                        </Text>
                        <TimeSlotPicker
                            timeSlots={timeSlotsData?.time_slots || []}
                            selectedSlot={selectedSlot}
                            onSlotSelect={setSelectedSlot}
                            isLoading={loadingSlots}
                        />
                    </View>
                )}

                <View className="flex-row gap-3">
                    <Button
                        title="Cancelar"
                        variant="outline"
                        className="flex-1"
                        onPress={onClose}
                    />
                    <Button
                        title="Solicitar"
                        className="flex-1"
                        onPress={handleConfirm}
                        disabled={!canConfirm}
                        loading={isSubmitting}
                    />
                </View>
            </View>
        </BottomSheet>
    );
}
