/**
 * GoDrive Mobile - TimeSlotPicker Component
 *
 * Grid de horários disponíveis para seleção.
 * Exibe horários em cards com estados: disponível, indisponível, selecionado.
 */

import React from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { Clock } from 'lucide-react-native';

import { TimeSlot } from '../api/schedulingApi';

interface TimeSlotPickerProps {
    timeSlots: TimeSlot[];
    selectedSlot: TimeSlot | null;
    onSlotSelect: (slot: TimeSlot) => void;
    isLoading?: boolean;
}

export function TimeSlotPicker({
    timeSlots,
    selectedSlot,
    onSlotSelect,
    isLoading = false,
}: TimeSlotPickerProps) {
    // Filtrar apenas horários disponíveis para exibição principal
    const availableSlots = timeSlots.filter(slot => slot.is_available);
    const unavailableSlots = timeSlots.filter(slot => !slot.is_available);

    // Verificar se um slot está selecionado
    const isSelected = (slot: TimeSlot): boolean => {
        return selectedSlot?.start_time === slot.start_time;
    };

    if (isLoading) {
        return (
            <View className="py-8">
                <View className="flex-row flex-wrap justify-start gap-3">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                        <View
                            key={i}
                            className="w-[30%] h-14 rounded-xl bg-neutral-100 animate-pulse"
                        />
                    ))}
                </View>
            </View>
        );
    }

    if (timeSlots.length === 0) {
        return (
            <View className="py-8 items-center">
                <Clock size={32} color="#9CA3AF" />
                <Text className="text-gray-500 mt-2 text-center">
                    Nenhum horário disponível{'\n'}para esta data
                </Text>
            </View>
        );
    }

    if (availableSlots.length === 0) {
        return (
            <View className="py-8 items-center">
                <Clock size={32} color="#9CA3AF" />
                <Text className="text-gray-500 mt-2 text-center">
                    Todos os horários estão{'\n'}ocupados nesta data
                </Text>
            </View>
        );
    }

    return (
        <View>
            {/* Horários disponíveis */}
            <View className="flex-row flex-wrap" style={{ gap: 12 }}>
                {timeSlots.map((slot) => {
                    const selected = isSelected(slot);
                    const available = slot.is_available;

                    return (
                        <TouchableOpacity
                            key={slot.start_time}
                            disabled={!available}
                            onPress={() => onSlotSelect(slot)}
                            className={`w-[30%] py-3 px-2 rounded-xl border items-center ${selected
                                    ? 'bg-primary-600 border-primary-600'
                                    : available
                                        ? 'bg-white border-neutral-200 active:border-primary-300 active:bg-primary-50'
                                        : 'bg-neutral-50 border-neutral-100'
                                }`}
                            accessibilityLabel={`Horário ${slot.start_time}${available ? '' : ', indisponível'}`}
                        >
                            <Text
                                className={`text-sm font-semibold ${selected
                                        ? 'text-white'
                                        : available
                                            ? 'text-gray-900'
                                            : 'text-gray-400 line-through'
                                    }`}
                            >
                                {slot.start_time}
                            </Text>
                            <Text
                                className={`text-xs mt-0.5 ${selected
                                        ? 'text-primary-100'
                                        : available
                                            ? 'text-gray-500'
                                            : 'text-gray-300'
                                    }`}
                            >
                                {slot.end_time}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </View>

            {/* Legenda */}
            <View className="flex-row items-center justify-center mt-4 gap-4">
                <View className="flex-row items-center">
                    <View className="w-3 h-3 rounded-full bg-primary-600 mr-1.5" />
                    <Text className="text-xs text-gray-500">Selecionado</Text>
                </View>
                <View className="flex-row items-center">
                    <View className="w-3 h-3 rounded-full bg-white border border-neutral-200 mr-1.5" />
                    <Text className="text-xs text-gray-500">Disponível</Text>
                </View>
                <View className="flex-row items-center">
                    <View className="w-3 h-3 rounded-full bg-neutral-100 mr-1.5" />
                    <Text className="text-xs text-gray-500">Ocupado</Text>
                </View>
            </View>
        </View>
    );
}
