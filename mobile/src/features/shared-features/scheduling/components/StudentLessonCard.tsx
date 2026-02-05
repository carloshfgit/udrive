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
        switch (status.toLowerCase()) {
            case 'confirmed': return 'info';
            case 'pending': return 'warning';
            case 'completed': return 'success';
            case 'canceled': return 'error';
            default: return 'default';
        }
    };

    const getStatusLabel = (status: string): string => {
        switch (status.toLowerCase()) {
            case 'confirmed': return 'Confirmada';
            case 'pending': return 'Pendente';
            case 'completed': return 'Concluída';
            case 'canceled': return 'Cancelada';
            default: return status;
        }
    };

    return (
        <View className="bg-white rounded-2xl p-4 mb-4 border border-neutral-100 shadow-sm">
            <View className="flex-row items-center mb-4">
                {/* Destaque Temporal */}
                <View className="bg-primary-50 px-3 py-2 rounded-xl items-center justify-center mr-4 w-16">
                    <Text className="text-primary-700 font-bold text-lg leading-tight">
                        {day}
                    </Text>
                    <Text className="text-primary-600 text-[10px] font-bold uppercase tracking-wider">
                        {month}
                    </Text>
                </View>

                {/* Info do Instrutor */}
                <View className="flex-1 flex-row items-center">
                    <Avatar
                        fallback={scheduling.instructor_name || 'I'}
                        size="md"
                    />
                    <View className="ml-3 flex-1">
                        <Text className="text-neutral-900 font-bold text-base" numberOfLines={1}>
                            {scheduling.instructor_name || 'Instrutor'}
                        </Text>
                        <View className="flex-row items-center mt-0.5">
                            <Clock size={12} color="#6B7280" />
                            <Text className="text-neutral-500 text-xs ml-1">
                                {hours}:{minutes} • {scheduling.duration_minutes} min
                            </Text>
                        </View>
                    </View>
                </View>

                <Badge
                    label={getStatusLabel(scheduling.status)}
                    variant={getStatusVariant(scheduling.status)}
                />
            </View>

            <View className="flex-row justify-between items-center pt-3 border-t border-neutral-50">
                <View className="flex-row items-center">
                    <Calendar size={14} color="#6B7280" />
                    <Text className="text-neutral-500 text-xs ml-1">
                        {weekDay}, {day} de {monthFull}
                    </Text>
                </View>

                <TouchableOpacity
                    onPress={() => onPressDetails(scheduling)}
                    className="flex-row items-center"
                    activeOpacity={0.6}
                >
                    <Text className="text-primary-600 font-semibold text-sm mr-1">
                        Ver Detalhes
                    </Text>
                    <ChevronRight size={16} color="#2563EB" />
                </TouchableOpacity>
            </View>
        </View>
    );
}
