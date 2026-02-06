import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Calendar, Clock, ChevronRight } from 'lucide-react-native';
import { Avatar } from '../../../../shared/components/Avatar';
import { Badge, BadgeVariant } from '../../../../shared/components/Badge';
import { BookingResponse } from '../api/schedulingApi';

interface StudentLessonCardProps {
    scheduling: BookingResponse;
    onPressDetails: (scheduling: BookingResponse) => void;
}

const WEEK_DAYS = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
const MONTHS = [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
];
const MONTHS_FULL = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
];

export function StudentLessonCard({ scheduling, onPressDetails }: StudentLessonCardProps) {
    const scheduledDate = new Date(scheduling.scheduled_datetime);

    // Fallback for parsing ISO string if Date constructor fails in some RN versions
    // Though usually new Date("ISO_STRING") works fine.

    const day = scheduledDate.getDate();
    const month = MONTHS[scheduledDate.getMonth()];
    const monthFull = MONTHS_FULL[scheduledDate.getMonth()];
    const weekDay = WEEK_DAYS[scheduledDate.getDay()];
    const hours = scheduledDate.getHours().toString().padStart(2, '0');
    const minutes = scheduledDate.getMinutes().toString().padStart(2, '0');

    const getStatusVariant = (status: string): BadgeVariant => {
        const s = status.toLowerCase();
        switch (s) {
            case 'confirmed': return 'success';
            case 'pending': return 'warning';
            case 'completed': return 'success';
            case 'canceled':
            case 'cancelled':
                return 'error';
            default: return 'default';
        }
    };

    const getStatusLabel = (status: string): string => {
        const s = status.toLowerCase();
        switch (s) {
            case 'confirmed': return 'Confirmada';
            case 'pending': return 'Pendente';
            case 'completed': return 'Concluída';
            case 'canceled':
            case 'cancelled':
                return 'Cancelada';
            default: return status;
        }
    };

    return (
        <View className="bg-white rounded-3xl p-6 mb-5 border border-neutral-100 shadow-md">
            {/* Top Section: Date, Time and Status */}
            <View className="flex-row justify-between items-start mb-6">
                <View className="flex-row items-center flex-1">
                    {/* Destaque Temporal */}
                    <View className="bg-primary-50 px-4 py-3 rounded-2xl items-center justify-center mr-5 min-w-[75px]">
                        <Text className="text-primary-700 font-black text-2xl leading-none">
                            {day}
                        </Text>
                        <Text className="text-primary-500 text-[10px] font-black uppercase tracking-widest mt-1">
                            {month}
                        </Text>
                    </View>

                    {/* Horário Destacado */}
                    <View className="flex-1">
                        <Text className="text-neutral-400 text-[10px] uppercase font-bold tracking-[2px] mb-1">
                            HORÁRIO
                        </Text>
                        <View className="flex-row items-baseline">
                            <Text className="text-neutral-900 font-black text-4xl tracking-tight">
                                {hours}:{minutes}
                            </Text>
                            <Text className="text-neutral-400 font-bold text-sm ml-2">
                                {scheduling.duration_minutes}m
                            </Text>
                        </View>
                    </View>
                </View>

                <Badge
                    label={getStatusLabel(scheduling.status)}
                    variant={getStatusVariant(scheduling.status)}
                    className="mt-1"
                />
            </View>

            {/* Middle Section: Instructor Info */}
            <View className="flex-row items-center bg-neutral-50/50 p-4 rounded-2xl mb-6">
                <Avatar
                    fallback={scheduling.instructor_name || 'I'}
                    size="lg"
                    className="border-2 border-white shadow-sm"
                />
                <View className="ml-4 flex-1">
                    <Text className="text-neutral-400 text-[10px] uppercase font-bold tracking-wider mb-1">
                        INSTRUTOR
                    </Text>
                    <Text className="text-neutral-800 font-bold text-lg" numberOfLines={1}>
                        {scheduling.instructor_name || 'Instrutor'}
                    </Text>
                </View>
            </View>

            {/* Bottom Section: Footer Info and Action */}
            <View className="flex-row justify-between items-center pt-4 border-t border-neutral-100">
                <View className="flex-row items-center">
                    <Calendar size={16} color="#9CA3AF" />
                    <Text className="text-neutral-500 text-sm font-medium ml-2 uppercase tracking-wide">
                        {weekDay}, {monthFull}
                    </Text>
                </View>

                <TouchableOpacity
                    onPress={() => onPressDetails(scheduling)}
                    className="bg-primary-600 px-5 py-2.5 rounded-xl shadow-sm shadow-primary-200"
                    activeOpacity={0.8}
                >
                    <Text className="text-white font-bold text-sm">
                        Ver Detalhes
                    </Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}
