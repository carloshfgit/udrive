/**
 * GoDrive Mobile - RescheduleDetailsScreen
 *
 * Tela para o instrutor revisar e responder a uma solicitação de reagendamento.
 */

import React, { useState } from 'react';
import { View, Text, SafeAreaView, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Calendar, Clock, AlertCircle } from 'lucide-react-native';
import { Header } from '../../../shared/components/Header';
import { Button } from '../../../shared/components/Button';
import { Card } from '../../../shared/components/Card';
import { Badge } from '../../../shared/components/Badge';
import { useAuth } from '../../auth/hooks/useAuth';
import { useRespondReschedule } from '../hooks/useInstructorSchedule';
import { Scheduling } from '../api/scheduleApi';

export function RescheduleDetailsScreen() {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { scheduling }: { scheduling: Scheduling } = route.params;
    const { user } = useAuth();
    const isSelfRequested = scheduling.rescheduled_by === user?.id;

    const respondMutation = useRespondReschedule();
    const [isSubmitting, setIsSubmitting] = useState(false);

    const originalDate = new Date(scheduling.scheduled_datetime);
    const newDate = scheduling.rescheduled_datetime ? new Date(scheduling.rescheduled_datetime) : null;

    const formatDate = (date: Date) => {
        return date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const handleResponse = async (accepted: boolean) => {
        const action = accepted ? 'aceitar' : 'recusar';
        Alert.alert(
            `${accepted ? 'Aceitar' : 'Recusar'} Reagendamento`,
            `Deseja realmente ${action} esta sugestão de novo horário?`,
            [
                { text: 'Voltar', style: 'cancel' },
                {
                    text: accepted ? 'Sim, Aceitar' : 'Sim, Recusar',
                    style: accepted ? 'default' : 'destructive',
                    onPress: async () => {
                        setIsSubmitting(true);
                        try {
                            await respondMutation.mutateAsync({
                                schedulingId: scheduling.id,
                                accepted
                            });
                            Alert.alert('Sucesso', `O reagendamento foi ${accepted ? 'aceito' : 'recusado'} com sucesso.`);
                            navigation.goBack();
                        } catch (error: any) {
                            Alert.alert('Erro', error.message || 'Ocorreu um erro ao processar a resposta.');
                        } finally {
                            setIsSubmitting(false);
                        }
                    }
                }
            ]
        );
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            <Header title="Detalhes do Reagendamento" onBack={() => navigation.goBack()} />

            <ScrollView className="flex-1 px-6 pt-4" showsVerticalScrollIndicator={false}>
                <View className="items-center mb-6">
                    <Badge label="REAGENDAMENTO SOLICITADO" variant="warning" />
                </View>

                <Text className="text-neutral-500 text-center mb-8">
                    {isSelfRequested ? (
                        "Você sugeriu um novo horário para esta aula. Aguardando resposta do aluno."
                    ) : (
                        <>
                            O aluno <Text className="font-bold text-neutral-900">{scheduling.student_name || 'Aluno'}</Text> solicitou a alteração do horário da aula.
                        </>
                    )}
                </Text>

                {/* Comparação de Horários */}
                <View className="gap-6">
                    <Card variant="outlined" className="p-4 border-neutral-200">
                        <Text className="text-neutral-400 text-xs font-bold uppercase tracking-widest mb-3">HORÁRIO ORIGINAL</Text>
                        <View className="flex-row items-center">
                            <Calendar size={20} color="#9CA3AF" className="mr-3" />
                            <Text className="text-neutral-600 line-through">{formatDate(originalDate)}</Text>
                        </View>
                    </Card>

                    <View className="items-center">
                        <View className="bg-amber-100 p-2 rounded-full">
                            <Clock size={24} color="#D97706" />
                        </View>
                    </View>

                    <Card variant="outlined" className="p-4 border-amber-200 bg-amber-50">
                        <Text className="text-amber-600 text-xs font-bold uppercase tracking-widest mb-3">NOVO HORÁRIO PROPOSTO</Text>
                        <View className="flex-row items-center">
                            <Calendar size={20} color="#D97706" className="mr-3" />
                            <Text className="text-neutral-900 font-bold text-lg">
                                {newDate ? formatDate(newDate) : 'Não informado'}
                            </Text>
                        </View>
                    </Card>
                </View>

                <View className="mt-8 bg-neutral-50 p-4 rounded-2xl flex-row items-center border border-neutral-100">
                    <AlertCircle size={20} color="#6B7280" />
                    <Text className="text-neutral-500 text-xs ml-3 flex-1">
                        {isSelfRequested
                            ? "Ao cancelar, o horário original da aula será mantido e a solicitação será removida."
                            : "Ao aceitar, o horário da aula será atualizado automaticamente. Ao recusar, o horário original será mantido."}
                    </Text>
                </View>

                {/* Botões de Ação */}
                <View className="flex-row gap-4 mt-10 mb-10">
                    {isSelfRequested ? (
                        <Button
                            title="Cancelar Solicitação"
                            variant="outline"
                            className="flex-1 border-red-200"
                            textClassName="text-red-500"
                            onPress={() => handleResponse(false)}
                            loading={isSubmitting}
                            disabled={isSubmitting}
                        />
                    ) : (
                        <>
                            <Button
                                title="Recusar"
                                variant="outline"
                                className="flex-1 border-red-200"
                                onPress={() => handleResponse(false)}
                                disabled={isSubmitting}
                            />
                            <Button
                                title="Aceitar Novo Horário"
                                className="flex-[2]"
                                onPress={() => handleResponse(true)}
                                loading={isSubmitting}
                                disabled={isSubmitting}
                            />
                        </>
                    )}
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
