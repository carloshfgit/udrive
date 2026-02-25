import React, { useState, useEffect } from 'react';
import { View, Text, SafeAreaView, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useRoute, useNavigation, useFocusEffect } from '@react-navigation/native';
import { Calendar, Clock, User, ChevronRight, MessageSquare, AlertCircle, CheckCircle2 } from 'lucide-react-native';
import { Header } from '../../../../shared/components/Header';
import { Button } from '../../../../shared/components/Button';
import { Avatar } from '../../../../shared/components/Avatar';
import { Badge, BadgeVariant } from '../../../../shared/components/Badge';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { useLessonDetails } from '../../../shared-features/scheduling/hooks/useLessonDetails';
import { RescheduleModal } from '../components/RescheduleModal';
import { LessonEvaluationModal } from '../components/LessonEvaluationModal';

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
        respondReschedule,
        isRespondingReschedule,
        refetch
    } = useLessonDetails(schedulingId);

    const [isRescheduleVisible, setIsRescheduleVisible] = useState(false);
    const [isEvaluationVisible, setIsEvaluationVisible] = useState(false);



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
        if (status.toLowerCase() === 'reschedule_requested') return 'REAGENDAMENTO';
        return status.toUpperCase();
    };

    const handleStart = () => {
        Alert.alert(
            "Iniciar Aula",
            "Deseja iniciar o cronômetro desta aula agora?",
            [
                { text: "Cancelar", style: "cancel" },
                {
                    text: "Sim, Iniciar",
                    onPress: () => startLesson(undefined, {
                        onError: (error: any) => {
                            const errorMessage = error.response?.data?.detail || error.message || 'Não foi possível iniciar a aula.';
                            Alert.alert("Erro", errorMessage);
                        }
                    })
                }
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
            message += "\n\nAtenção: Faltam menos de 24h para a aula. Não há direito a reembolso (0%).";
        } else if (diffHours < 48) {
            message += "\n\nAtenção: Faltam entre 24h e 48h para a aula. Haverá retenção de 50% como taxa de reserva.";
        } else {
            message += "\n\nCancelamento gratuito disponível (reembolso integral de 100%).";
        }

        Alert.alert("Confirmar Cancelamento", message, [
            { text: "Manter Aula", style: "cancel" },
            {
                text: "Confirmar Cancelamento",
                style: "destructive",
                onPress: () => cancelLesson(undefined, {
                    onError: (error: any) => {
                        const errorMessage = error.response?.data?.detail || error.message || 'Não foi possível cancelar a aula.';
                        Alert.alert("Erro", errorMessage);
                    }
                })
            }
        ]);
    };

    const handleFinish = () => {
        Alert.alert(
            "Concluir Aula",
            "Deseja marcar esta aula como concluída?",
            [
                { text: "Cancelar", style: "cancel" },
                {
                    text: "Sim, Concluir",
                    onPress: () => completeLesson(undefined, {
                        onSuccess: () => {
                            setIsEvaluationVisible(true);
                        },
                        onError: (error: any) => {
                            const errorMessage = error.response?.data?.detail || error.message || 'Não foi possível concluir a aula.';
                            Alert.alert('Erro', errorMessage);
                        }
                    })
                }
            ]
        );
    };

    const handleConfirmReschedule = async (newDatetime: string) => {
        try {
            // Usar a versão async da mutation para capturar erros corretamente
            await requestReschedule(newDatetime);
            setIsRescheduleVisible(false);
            Alert.alert("Sucesso", "Solicitação de reagendamento enviada com sucesso!");
        } catch (error: any) {
            console.error('Erro ao reagendar:', error);
            Alert.alert("Erro", error.message || "Não foi possível solicitar o reagendamento.");
        }
    };

    const handleRespondReschedule = async (accepted: boolean) => {
        try {
            await respondReschedule(accepted);
            Alert.alert(
                accepted ? "Sucesso" : "Recusado",
                accepted ? "Reagendamento aceito com sucesso!" : "O pedido de reagendamento foi recusado."
            );
        } catch (error: any) {
            console.error('Erro ao responder reagendamento:', error);
            Alert.alert("Erro", error.message || "Não foi possível responder ao reagendamento.");
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
                {/* Proposed Time Highlight Card */}
                {lesson.status.toLowerCase() === 'reschedule_requested' && lesson.rescheduled_datetime && (
                    <View className="bg-amber-50 border-2 border-amber-200 rounded-3xl p-5 mb-8 shadow-sm scale-[1.02]">
                        <View className="flex-row items-center mb-3">
                            <View className="bg-amber-100 p-2 rounded-xl mr-3">
                                <Clock size={20} color="#D97706" />
                            </View>
                            <Text className="text-amber-800 font-black text-[10px] uppercase tracking-[2px]">
                                NOVA PROPOSTA DE HORÁRIO
                            </Text>
                        </View>

                        <View className="flex-row items-center justify-between">
                            <View className="flex-1">
                                <Text className="text-neutral-900 font-black text-2xl">
                                    {new Date(lesson.rescheduled_datetime).toLocaleDateString('pt-BR', { day: '2-digit', month: 'long' })}
                                </Text>
                                <Text className="text-primary-600 font-black text-4xl tracking-tighter mt-1">
                                    {new Date(lesson.rescheduled_datetime).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                                </Text>
                            </View>

                            <View className="bg-amber-200/30 px-3 py-1 rounded-full border border-amber-200">
                                <Text className="text-amber-700 text-[10px] font-bold">SUGESTÃO</Text>
                            </View>
                        </View>

                        <View className="mt-4 pt-4 border-t border-amber-200/50">
                            <Text className="text-amber-800 text-xs font-medium leading-5">
                                {lesson.rescheduled_by === lesson.instructor_id
                                    ? "O instrutor propôs este novo horário. Deslize a tela para baixo para aceitar ou recusar."
                                    : "Você sugeriu este novo horário. O instrutor foi notificado e responderá em breve."}
                            </Text>
                        </View>
                    </View>
                )}

                {/* Main Info Card */}
                <View className={`bg-neutral-50 rounded-3xl p-6 mb-8 border border-neutral-100 ${lesson.status.toLowerCase() === 'reschedule_requested' ? 'opacity-60' : ''}`}>
                    <View className="flex-row items-center mb-6">
                        <View className={`p-3 rounded-2xl mr-4 ${lesson.status.toLowerCase() === 'reschedule_requested' ? 'bg-neutral-200' : 'bg-primary-50'}`}>
                            <Calendar size={24} color={lesson.status.toLowerCase() === 'reschedule_requested' ? '#6B7280' : '#2563EB'} />
                        </View>
                        <View>
                            <Text className="text-neutral-400 text-xs font-bold uppercase tracking-wider">
                                {lesson.status.toLowerCase() === 'reschedule_requested' ? 'HORÁRIO ORIGINAL' : 'DATA'}
                            </Text>
                            <Text className={`font-bold text-lg ${lesson.status.toLowerCase() === 'reschedule_requested' ? 'text-neutral-500 line-through' : 'text-neutral-900'}`}>
                                {day} de {month}, {year}
                            </Text>
                        </View>
                    </View>

                    <View className="flex-row items-center">
                        <View className={`p-3 rounded-2xl mr-4 ${lesson.status.toLowerCase() === 'reschedule_requested' ? 'bg-neutral-200' : 'bg-primary-50'}`}>
                            <Clock size={24} color={lesson.status.toLowerCase() === 'reschedule_requested' ? '#6B7280' : '#2563EB'} />
                        </View>
                        <View>
                            <Text className="text-neutral-400 text-xs font-bold uppercase tracking-wider">HORÁRIO E DURAÇÃO</Text>
                            <Text className={`font-bold text-lg ${lesson.status.toLowerCase() === 'reschedule_requested' ? 'text-neutral-500 line-through' : 'text-neutral-900'}`}>
                                {hours}:{minutes} • {lesson.duration_minutes} minutos
                            </Text>
                        </View>
                    </View>
                </View>

                {/* Instructor Block */}
                <Text className="text-neutral-900 font-black text-xl mb-4">Instrutor</Text>
                <View className="bg-white rounded-3xl p-5 mb-8 border border-neutral-100 shadow-sm">
                    <TouchableOpacity
                        onPress={() => navigation.navigate('InstructorProfile', { instructorId: lesson.instructor_id })}
                        className="flex-row items-center mb-5"
                    >
                        <Avatar
                            fallback={lesson.instructor_name || 'I'}
                            size="xl"
                        />
                        <View className="ml-4 flex-1">
                            <Text className="text-neutral-900 font-bold text-xl">{lesson.instructor_name || 'Instrutor'}</Text>
                            <View className="flex-row items-center mt-1">
                                <Text className="text-amber-500 font-bold">★ {lesson.instructor_rating?.toFixed(1) || '0.0'}</Text>
                                <Text className="text-neutral-400 text-sm ml-1">({lesson.instructor_review_count || 0} avaliações)</Text>
                            </View>
                        </View>
                        <ChevronRight size={20} color="#9CA3AF" />
                    </TouchableOpacity>

                    {!['completed', 'canceled', 'cancelled'].includes(lesson.status.toLowerCase()) && (
                        <View className="flex-row gap-3">
                            <Button
                                title="Chat com Instrutor"
                                variant="ghost"
                                leftIcon={<MessageSquare size={20} color="#2563EB" />}
                                className="flex-1"
                                onPress={() => navigation.navigate('ChatRoom', {
                                    otherUserId: lesson.instructor_id,
                                    otherUserName: lesson.instructor_name || 'Instrutor',
                                })}
                            />
                        </View>
                    )}
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

                            {!lesson.has_review && (
                                <View className="w-full mt-6">
                                    <Button
                                        title="Avaliar Aula"
                                        onPress={() => setIsEvaluationVisible(true)}
                                        variant="primary"
                                        size="md"
                                        fullWidth
                                    />
                                </View>
                            )}
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
                        <View className="bg-amber-50 rounded-2xl p-4 mb-2 border border-amber-100">
                            <View className="flex-row items-center mb-3">
                                <AlertCircle size={20} color="#D97706" />
                                <Text className="text-amber-700 text-sm ml-3 flex-1 font-medium">
                                    {lesson.rescheduled_by === lesson.instructor_id
                                        ? "O instrutor propôs um novo horário para esta aula."
                                        : "Você solicitou um reagendamento. Aguarde a aprovação do instrutor."}
                                </Text>
                            </View>

                            {lesson.rescheduled_by === lesson.instructor_id && (
                                <View className="flex-row gap-3">
                                    <Button
                                        title="Recusar"
                                        variant="outline"
                                        className="flex-1"
                                        onPress={() => handleRespondReschedule(false)}
                                        loading={isRespondingReschedule}
                                        size="sm"
                                    />
                                    <Button
                                        title="Aceitar"
                                        className="flex-1"
                                        onPress={() => handleRespondReschedule(true)}
                                        loading={isRespondingReschedule}
                                        size="sm"
                                    />
                                </View>
                            )}
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
                            variant="ghost"
                            textClassName="text-warning-600 font-bold"
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
                                textClassName="text-red-600"
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

            <LessonEvaluationModal
                visible={isEvaluationVisible}
                onClose={() => setIsEvaluationVisible(false)}
                scheduling={lesson}
                onSuccess={() => {
                    refetch();
                    Alert.alert("Sucesso", "Obrigado por sua avaliação!");
                }}
            />
        </SafeAreaView>
    );
}
