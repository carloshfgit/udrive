/**
 * GoDrive Mobile - BookingSummary Component
 *
 * Card de resumo do agendamento exibindo instrutor, data, horário e preço.
 */

import React from 'react';
import { View, Text } from 'react-native';
import { Calendar, Clock, DollarSign, User, Car, Bike } from 'lucide-react-native';

import { Avatar } from '../../../../shared/components';
import { formatPrice } from '../../../../shared';

interface BookingSummaryProps {
    instructorName: string;
    instructorAvatar?: string | null;
    date: Date;
    startTime: string;
    endTime: string;
    durationMinutes: number;
    price: number;
    licenseCategory?: string;
    lessonCategory?: string;
    vehicleOwnership?: string;
}

// Formatadores
const formatDate = (date: Date): string => {
    const options: Intl.DateTimeFormatOptions = {
        weekday: 'long',
        day: '2-digit',
        month: 'long',
    };
    return date.toLocaleDateString('pt-BR', options);
};



export function BookingSummary({
    instructorName,
    instructorAvatar,
    date,
    startTime,
    endTime,
    durationMinutes,
    price,
    licenseCategory,
    lessonCategory,
    vehicleOwnership,
}: BookingSummaryProps) {
    const formattedDate = formatDate(date);
    const formattedPrice = formatPrice(price);
    const hours = durationMinutes / 60;
    const durationLabel = hours === 1 ? '1 hora' : `${hours} horas`;

    return (
        <View className="bg-white rounded-2xl border border-neutral-100 p-4">
            {/* Header - Instrutor */}
            <View className="flex-row items-center pb-4 border-b border-neutral-100">
                <Avatar
                    source={instructorAvatar ? { uri: instructorAvatar } : undefined}
                    fallback={instructorName.charAt(0)}
                    size="lg"
                />
                <View className="flex-1 ml-3">
                    <Text className="text-base font-semibold text-gray-900">
                        {instructorName}
                    </Text>
                    {(lessonCategory || vehicleOwnership) && (
                        <View className="flex-row items-center mt-1 gap-2">
                            {lessonCategory && (
                                <View className="bg-primary-50 px-2 py-0.5 rounded-full flex-row items-center">
                                    {lessonCategory === 'A' ? (
                                        <Bike size={12} color="#2563EB" />
                                    ) : (
                                        <Car size={12} color="#2563EB" />
                                    )}
                                    <Text className="text-xs font-medium text-primary-700 ml-1">
                                        Cat. {lessonCategory}
                                    </Text>
                                </View>
                            )}
                            {vehicleOwnership && (
                                <View className="bg-emerald-50 px-2 py-0.5 rounded-full">
                                    <Text className="text-xs font-medium text-emerald-700">
                                        {vehicleOwnership === 'instructor'
                                            ? 'Veículo do instrutor'
                                            : 'Meu veículo'}
                                    </Text>
                                </View>
                            )}
                        </View>
                    )}
                </View>
            </View>

            {/* Detalhes do agendamento */}
            <View className="pt-4 gap-3">
                {/* Data */}
                <View className="flex-row items-center">
                    <View className="w-10 h-10 rounded-full bg-primary-50 items-center justify-center">
                        <Calendar size={18} color="#2563EB" />
                    </View>
                    <View className="ml-3">
                        <Text className="text-xs text-gray-500">Data</Text>
                        <Text className="text-sm font-medium text-gray-900 capitalize">
                            {formattedDate}
                        </Text>
                    </View>
                </View>

                {/* Horário */}
                <View className="flex-row items-center">
                    <View className="w-10 h-10 rounded-full bg-primary-50 items-center justify-center">
                        <Clock size={18} color="#2563EB" />
                    </View>
                    <View className="ml-3">
                        <Text className="text-xs text-gray-500">Horário</Text>
                        <Text className="text-sm font-medium text-gray-900">
                            {startTime} - {endTime} ({durationLabel})
                        </Text>
                    </View>
                </View>

                {/* Preço */}
                <View className="flex-row items-center">
                    <View className="w-10 h-10 rounded-full bg-success-50 items-center justify-center">
                        <DollarSign size={18} color="#16A34A" />
                    </View>
                    <View className="ml-3">
                        <Text className="text-xs text-gray-500">Valor da Aula</Text>
                        <Text className="text-sm font-semibold text-success-600">
                            {formattedPrice}
                        </Text>
                    </View>
                </View>
            </View>
        </View>
    );
}
