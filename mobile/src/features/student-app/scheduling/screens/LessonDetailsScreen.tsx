import React, { useState, useEffect } from 'react';
import { View, Text, SafeAreaView, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Calendar, Clock, User, ChevronRight, MessageSquare, AlertCircle } from 'lucide-react-native';
import { Header } from '../../../../shared/components/Header';
import { Button } from '../../../../shared/components/Button';
import { Avatar } from '../../../../shared/components/Avatar';
import { Badge, BadgeVariant } from '../../../../shared/components/Badge';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { useLessonDetails } from '../../../shared-features/scheduling/hooks/useLessonDetails';

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
        refetch
    } = useLessonDetails(schedulingId);

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
        if (s === 'completed') return 'success';
        if (s === 'canceled' || s === 'cancelled') return 'error';
        return 'default';
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

    return (
        <SafeAreaView className="flex-1 bg-white">
            <Header title="Detalhes da Aula" onBack={() => navigation.goBack()} />

            <ScrollView className="flex-1 px-6 pt-4" showsVerticalScrollIndicator={false}>
                {/* Status Badge */}
                <View className="items-center mb-6">
                    <Badge
                        label={lesson.status.toUpperCase()}
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
                    {lesson.status.toLowerCase() === 'pending' && (
                        <View className="bg-amber-50 p-4 rounded-2xl flex-row items-center mb-2 border border-amber-100">
                            <AlertCircle size={20} color="#D97706" />
                            <Text className="text-amber-700 text-sm ml-3 flex-1 font-medium">
                                Aguardando confirmação do instrutor para liberar o início da aula.
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
        </SafeAreaView>
    );
}
