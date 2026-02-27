/**
 * ScheduleCard
 *
 * Componente de card de agendamento usado na agenda do instrutor.
 */

import React from 'react';
import {
    View,
    Text,
    TouchableOpacity,
    ActivityIndicator,
    Alert,
} from 'react-native';
import {
    Clock,
    Check,
    User,
    MessageSquare,
    Car,
    Award,
    Bike,
} from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';
import { Card } from '../../../shared/components';
import { Scheduling, SchedulingStatus } from '../api/scheduleApi';
import { useAuth } from '../../auth/hooks/useAuth';

interface ScheduleCardProps {
    scheduling: Scheduling;
    onCancel: (id: string) => void;
    onReschedule: (scheduling: Scheduling) => void;
    isCancelling: boolean;
}

export function ScheduleCard({
    scheduling,
    onCancel,
    onReschedule,
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
                return { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200', accent: 'bg-yellow-500', icon: '#A16207', label: 'Pendente' };
            case 'confirmed':
                return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', accent: 'bg-emerald-500', icon: '#047857', label: 'Confirmado' };
            case 'completed':
                return { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', accent: 'bg-purple-500', icon: '#7E22CE', label: 'Concluído' };
            case 'cancelled':
                return { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', accent: 'bg-red-500', icon: '#B91C1C', label: 'Cancelado' };
            case 'reschedule_requested':
                return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', accent: 'bg-amber-500', icon: '#B45309', label: 'Reagendamento' };
            default:
                return { bg: 'bg-gray-50', text: 'text-gray-700', border: 'border-gray-200', accent: 'bg-gray-500', icon: '#374151', label: status };
        }
    };

    const statusInfo = getStatusColor(scheduling.status);


    const getVehicleLabel = (ownership?: string) => {
        if (ownership === 'instructor') return 'Veículo do Instrutor';
        if (ownership === 'student') return 'Veículo do Aluno';
        return 'Veículo não informado';
    };

    const getCategoryLabel = (category?: string) => {
        if (category === 'A') return 'A';
        if (category === 'B') return 'B';
        if (category === 'AB') return 'A+B';
        return category || 'B'; // Mantém 'B' como default para compatibilidade
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
                            <View className={`w-2 h-2 rounded-full ${statusInfo.accent} mr-2`} />
                            <Text className="text-sm text-gray-500">Valor da aula</Text>
                        </View>
                        <Text className="text-lg font-black text-gray-900">
                            R$ {Number(scheduling.price).toFixed(2)}
                        </Text>
                    </View>

                    {/* Informações da Aula (Categoria e Veículo) */}
                    {(scheduling.status === 'pending' || scheduling.status === 'confirmed' || scheduling.status === 'completed') && (
                        <View className={`flex-row items-center justify-around ${statusInfo.bg} border ${statusInfo.border} p-3 rounded-2xl mb-4`}>
                            <View className="flex-row items-center px-2">
                                <Award size={16} color={statusInfo.icon} />
                                <Text className={`font-bold ml-2 ${statusInfo.text}`}>
                                    Cat. {getCategoryLabel(scheduling.lesson_category)}
                                </Text>
                            </View>
                            <View className="flex-row items-center px-2">
                                {scheduling.lesson_category === 'A' ? (
                                    <Bike size={16} color={statusInfo.icon} />
                                ) : (
                                    <Car size={16} color={statusInfo.icon} />
                                )}
                                <Text className={`font-bold ml-2 ${statusInfo.text}`}>
                                    {getVehicleLabel(scheduling.vehicle_ownership)}
                                </Text>
                            </View>
                        </View>
                    )}

                    {scheduling.status === 'reschedule_requested' && (
                        <TouchableOpacity
                            onPress={() => navigation.navigate('InstructorSchedule', {
                                screen: 'RescheduleDetails',
                                params: { scheduling }
                            })}
                            className="flex-row items-center justify-center py-3.5 rounded-2xl bg-amber-500 active:bg-amber-600 shadow-sm"
                        >
                            <Clock size={18} color="#ffffff" />
                            <Text className="text-white font-bold ml-2">
                                {isSelfRequested ? 'Minha Sugestão' : 'Ver Solicitação'}
                            </Text>
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