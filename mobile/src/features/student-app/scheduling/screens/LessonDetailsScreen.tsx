import React, { useState, useEffect } from 'react';
import { View, Text, SafeAreaView, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Calendar, Clock, User, ChevronRight, MessageSquare, AlertCircle, CheckCircle2 } from 'lucide-react-native';
import { Header } from '../../../../shared/components/Header';
import { Button } from '../../../../shared/components/Button';
import { Avatar } from '../../../../shared/components/Avatar';
import { Badge, BadgeVariant } from '../../../../shared/components/Badge';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { useLessonDetails } from '../../../shared-features/scheduling/hooks/useLessonDetails';
import { RescheduleModal } from '../components/RescheduleModal';

export function LessonDetailsScreen() {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { schedulingId } = route.params;

    const {
        lesson,
        isLoading,
        isError,
        startLesson,
        isStarting,
        completeLesson,
        isCompleting,
        cancelLesson,
        isCancelling,
        requestReschedule,
        isRequestingReschedule,
        refetch
    } = useLessonDetails(schedulingId);

    const [isRescheduleVisible, setIsRescheduleVisible] = useState(false);

    if (isLoading) return <LoadingState.Card />;

    if (isError || !lesson) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <Header title="Detalhes da Aula" onBack={() => navigation.goBack()} />
                <EmptyState
                    title="Erro ao carregar"
                    message="Não foi possível encontrar os detalhes desta aula."
                    action={<Button title="Voltar" onPress={() => navigation.goBack()} />}
                />
            </SafeAreaView>
        );
    }

    const scheduledDate = new Date(lesson.scheduled_datetime);
    const day = scheduledDate.getDate();
    const month = scheduledDate.toLocaleDateString('pt-BR', { month: 'long' });
    const year = scheduledDate.getFullYear();
    const hours = scheduledDate.getHours().toString().padStart(2, '0');
    const minutes = scheduledDate.getMinutes().toString().padStart(2, '0');

    const getStatusVariant = (status: string): BadgeVariant => {
        const s = status.toLowerCase();
        if (s === 'confirmed') return 'success';
        if (s === 'pending') return 'warning';
        if (s === 'reschedule_requested') return 'warning';
        if (s === 'completed') return 'secondary';
        if (s === 'canceled' || s === 'cancelled') return 'error';
        return 'default';
    };

    const getStatusLabel = (status: string): string => {
        if (status.toLowerCase() === 'reschedule_requested') return 'REAGENDAMENTO SOLICITADO';
        return status.toUpperCase();
    };

    const handleStart = () => {
        Alert.alert(
            "Iniciar Aula",
            "Deseja iniciar o cronômetro desta aula agora?",
            [
                { text: "Cancelar", style: "cancel" },
                { text: "Sim, Iniciar", onPress: () => startLesson() }
            ]
        );
    };

    const handleCancel = () => {
        // Here we'd show the refund rules based on time
        const now = new Date().getTime();
        const lessonTime = scheduledDate.getTime();
        const diffHours = (lessonTime - now) / 3600000;

        let message = "Deseja realmente cancelar este agendamento?";
        if (diffHours < 24) {
            message += "\n\nAtenção: Falta menos de 24h para a aula. Haverá multa de 50%.";
        } else {
            message += "\n\nCancelamento gratuito disponível (reembolso 100%).";
        }

        Alert.alert("Confirmar Cancelamento", message, [
            { text: "Manter Aula", style: "cancel" },
            {
                text: "Confirmar Cancelamento",
                style: "destructive",
                onPress: () => cancelLesson(undefined)
            }
        ]);
    };

    const handleFinish = () => {
        Alert.alert(
            "Concluir Aula",
            "Deseja marcar esta aula como concluída?",
            [
                { text: "Cancelar", style: "cancel" },
                { text: "Sim, Concluir", onPress: () => completeLesson() }
            ]
        );
    };

    const handleConfirmReschedule = async (newDatetime: string) => {
        try {
            await requestReschedule(newDatetime);
            setIsRescheduleVisible(false);
            Alert.alert("Sucesso", "Solicitação de reagendamento enviada com sucesso!");
        } catch (error: any) {
            Alert.alert("Erro", error.message || "Não foi possível solicitar o reagendamento.");
        }
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            <Header title="Detalhes da Aula" onBack={() => navigation.goBack()} />

            <ScrollView className="flex-1 px-6 pt-4" showsVerticalScrollIndicator={false}>
                {/* Status Badge */}
                <View className="items-center mb-6">
                    <Badge
                        label={getStatusLabel(lesson.status)}
                        variant={getStatusVariant(lesson.status)}
                    />
                </View>

                {/* Main Info Card */}
                <View className="bg-neutral-50 rounded-3xl p-6 mb-8 border border-neutral-100">
                    <View className="flex-row items-center mb-6">
                        <View className="bg-primary-50 p-3 rounded-2xl mr-4">
                            <Calendar size={24} color="#2563EB" />
                        </View>
                        <View>
                            <Text className="text-neutral-400 text-xs font-bold uppercase tracking-wider">DATA</Text>
                            <Text className="text-neutral-900 font-bold text-lg">{day} de {month}, {year}</Text>
                        </View>
                    </View>

                    <View className="flex-row items-center">
                        <View className="bg-primary-50 p-3 rounded-2xl mr-4">
                            <Clock size={24} color="#2563EB" />
                        </View>
                        <View>
                            <Text className="text-neutral-400 text-xs font-bold uppercase tracking-wider">HORÁRIO E DURAÇÃO</Text>
                            <Text className="text-neutral-900 font-bold text-lg">{hours}:{minutes} • {lesson.duration_minutes} minutos</Text>
                        </View>
                    </View>

                    {lesson.status.toLowerCase() === 'reschedule_requested' && lesson.rescheduled_datetime && (
                        <View className="mt-4 pt-4 border-t border-neutral-100 italic">
                            <Text className="text-amber-600 text-sm font-medium">
                                Novo horário proposto: {new Date(lesson.rescheduled_datetime).toLocaleString('pt-BR', {
                                    day: '2-digit',
                                    month: 'long',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </Text>
                        </View>
                    )}
                </View>

                {/* Instructor Block */}
                <Text className="text-neutral-900 font-black text-xl mb-4">Instrutor</Text>
                <View className="bg-white rounded-3xl p-5 mb-8 border border-neutral-100 shadow-sm">
                    <View className="flex-row items-center mb-5">
                        <Avatar
                            fallback={lesson.instructor_name || 'I'}
                            size="xl"
                        />
                        <View className="ml-4 flex-1">
                            <Text className="text-neutral-900 font-bold text-xl">{lesson.instructor_name || 'Instrutor'}</Text>
                            <View className="flex-row items-center mt-1">
                                <Text className="text-amber-500 font-bold">★ 4.9</Text>
                                <Text className="text-neutral-400 text-sm ml-1">(128 avaliações)</Text>
                            </View>
                        </View>
                        <TouchableOpacity onPress={() => console.log('Ver Perfil')}>
                            <ChevronRight size={20} color="#9CA3AF" />
                        </TouchableOpacity>
                    </View>

                    <View className="flex-row gap-3">
                        <Button
                            title="Chat com Instrutor"
                            variant="outline"
                            className="flex-1"
                            onPress={() => Alert.alert("Em breve", "O sistema de chat está sendo implementado.")}
                        />
                    </View>
                </View>

                {/* Action Buttons Section */}
                <View className="mb-10 mt-4 gap-4">
                    {lesson.status.toLowerCase() === 'completed' && (
                        <View className="bg-green-50 p-6 rounded-3xl items-center border border-green-100">
                            <View className="bg-green-100 p-3 rounded-full mb-3">
                                <CheckCircle2 size={32} color="#16A34A" />
                            </View>
                            <Text className="text-green-900 font-bold text-lg text-center">
                                Parabéns! Você concluiu essa aula.
                            </Text>
                            <Text className="text-green-700 text-center mt-2">
                                Esperamos que tenha sido um ótimo aprendizado!
                            </Text>
                        </View>
                    )}

                    {lesson.status.toLowerCase() === 'pending' && (
                        <View className="bg-amber-50 p-4 rounded-2xl flex-row items-center mb-2 border border-amber-100">
                            <AlertCircle size={20} color="#D97706" />
                            <Text className="text-amber-700 text-sm ml-3 flex-1 font-medium">
                                Aguardando confirmação do instrutor para liberar o início da aula.
                            </Text>
                        </View>
                    )}

                    {lesson.status.toLowerCase() === 'reschedule_requested' && (
                        <View className="bg-amber-50 p-4 rounded-2xl flex-row items-center mb-2 border border-amber-100">
                            <AlertCircle size={20} color="#D97706" />
                            <Text className="text-amber-700 text-sm ml-3 flex-1 font-medium">
                                Você solicitou um reagendamento. Aguarde a aprovação do instrutor.
                            </Text>
                        </View>
                    )}

                    {lesson.status.toLowerCase() === 'confirmed' && !lesson.started_at && (
                        <Button
                            title="Iniciar Aula"
                            onPress={handleStart}
                            loading={isStarting}
                            size="lg"
                            fullWidth
                        />
                    )}

                    {lesson.status.toLowerCase() === 'confirmed' && lesson.started_at && (
                        <View className="gap-4">
                            <Button
                                title="Concluir Aula"
                                onPress={handleFinish}
                                loading={isCompleting}
                                variant="primary"
                                size="lg"
                                fullWidth
                            />
                        </View>
                    )}

                    {(lesson.status.toLowerCase() === 'pending' || lesson.status.toLowerCase() === 'confirmed') && (
                        <Button
                            title="Reagendar Aula"
                            variant="outline"
                            onPress={() => setIsRescheduleVisible(true)}
                            size="lg"
                            fullWidth
                        />
                    )}

                    {(lesson.status.toLowerCase() === 'pending' ||
                        lesson.status.toLowerCase() === 'confirmed' ||
                        lesson.status.toLowerCase() === 'reschedule_requested') && (
                            <Button
                                title="Cancelar Agendamento"
                                variant="ghost"
                                className="text-red-500"
                                onPress={handleCancel}
                                loading={isCancelling}
                                size="lg"
                                fullWidth
                            />
                        )}
                </View>
            </ScrollView>

            <RescheduleModal
                isVisible={isRescheduleVisible}
                onClose={() => setIsRescheduleVisible(false)}
                onConfirm={handleConfirmReschedule}
                instructorId={lesson.instructor_id}
                durationMinutes={lesson.duration_minutes}
                isSubmitting={isRequestingReschedule}
            />
        </SafeAreaView>
    );
}
