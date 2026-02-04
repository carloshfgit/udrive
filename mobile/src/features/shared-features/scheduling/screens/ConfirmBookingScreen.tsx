/**
 * GoDrive Mobile - ConfirmBookingScreen
 *
 * Tela de confirmação do agendamento antes de enviar.
 */

import React, { useState } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { ChevronLeft, AlertCircle, Info } from 'lucide-react-native';

import { BookingSummary } from '../components';
import { useCreateBooking } from '../hooks';
import { SchedulingStackParamList } from './SelectDateTimeScreen';

type ConfirmBookingRouteProp = RouteProp<SchedulingStackParamList, 'ConfirmBooking'>;
type ConfirmBookingNavigationProp = NativeStackNavigationProp<SchedulingStackParamList, 'ConfirmBooking'>;

export function ConfirmBookingScreen() {
    const navigation = useNavigation<ConfirmBookingNavigationProp>();
    const route = useRoute<ConfirmBookingRouteProp>();
    const {
        instructorId,
        instructorName,
        instructorAvatar,
        hourlyRate,
        licenseCategory,
        selectedDate,
        selectedSlot,
        durationMinutes,
    } = route.params;

    const [isSubmitting, setIsSubmitting] = useState(false);
    const createBookingMutation = useCreateBooking();

    // Calcular preço
    const hours = durationMinutes / 60;
    const totalPrice = hourlyRate * hours;

    // Converter data
    const dateObj = new Date(selectedDate);

    // Criar datetime para o backend
    // Envia com offset local para preservar o horário selecionado
    const createScheduledDatetime = (): string => {
        const [hours, minutes] = selectedSlot.start_time.split(':').map(Number);
        const scheduledDate = new Date(dateObj);
        scheduledDate.setHours(hours, minutes, 0, 0);

        // Formatar como ISO 8601 com offset local (não UTC)
        // Isso garante que 17:00 local seja enviado como 17:00-03:00, não 20:00Z
        const pad = (n: number) => n.toString().padStart(2, '0');
        const tzOffset = -scheduledDate.getTimezoneOffset(); // em minutos
        const tzSign = tzOffset >= 0 ? '+' : '-';
        const tzHours = pad(Math.floor(Math.abs(tzOffset) / 60));
        const tzMinutes = pad(Math.abs(tzOffset) % 60);

        const year = scheduledDate.getFullYear();
        const month = pad(scheduledDate.getMonth() + 1);
        const day = pad(scheduledDate.getDate());
        const hour = pad(scheduledDate.getHours());
        const minute = pad(scheduledDate.getMinutes());

        return `${year}-${month}-${day}T${hour}:${minute}:00${tzSign}${tzHours}:${tzMinutes}`;
    };

    // Handler para confirmar
    const handleConfirm = async () => {
        setIsSubmitting(true);

        try {
            const scheduledDatetime = createScheduledDatetime();

            const result = await createBookingMutation.mutateAsync({
                instructor_id: instructorId,
                scheduled_datetime: scheduledDatetime,
                duration_minutes: durationMinutes,
            });

            // Navegar para tela de sucesso
            navigation.navigate('BookingSuccess', {
                schedulingId: result.id,
                instructorName,
                scheduledDatetime,
            });
        } catch (error: any) {
            const message = error?.response?.data?.detail || 'Erro ao criar agendamento. Tente novamente.';
            Alert.alert('Erro', message);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
                <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    disabled={isSubmitting}
                    className="w-10 h-10 items-center justify-center"
                    accessibilityLabel="Voltar"
                >
                    <ChevronLeft size={24} color="#111318" />
                </TouchableOpacity>
                <Text className="flex-1 text-lg font-bold text-gray-900 text-center">
                    Confirmar Agendamento
                </Text>
                <View className="w-10" />
            </View>

            <ScrollView className="flex-1 px-6" showsVerticalScrollIndicator={false}>
                {/* Resumo do Agendamento */}
                <View className="pt-6">
                    <BookingSummary
                        instructorName={instructorName}
                        instructorAvatar={instructorAvatar}
                        date={dateObj}
                        startTime={selectedSlot.start_time}
                        endTime={selectedSlot.end_time}
                        durationMinutes={durationMinutes}
                        price={totalPrice}
                        licenseCategory={licenseCategory}
                    />
                </View>

                {/* Informações */}
                <View className="mt-6 p-4 bg-info-50 rounded-xl flex-row">
                    <Info size={20} color="#0369A1" />
                    <View className="flex-1 ml-3">
                        <Text className="text-sm font-medium text-info-700">
                            Ponto de Encontro
                        </Text>
                        <Text className="text-sm text-info-600 mt-1">
                            O instrutor entrará em contato para definir o local de encontro.
                        </Text>
                    </View>
                </View>

                {/* Política de Cancelamento */}
                <View className="mt-4 p-4 bg-warning-50 rounded-xl flex-row">
                    <AlertCircle size={20} color="#D97706" />
                    <View className="flex-1 ml-3">
                        <Text className="text-sm font-medium text-warning-700">
                            Política de Cancelamento
                        </Text>
                        <View className="mt-2">
                            <Text className="text-sm text-warning-600">
                                • Cancelamento gratuito até 24h antes da aula
                            </Text>
                            <Text className="text-sm text-warning-600 mt-1">
                                • Após 24h: multa de 50% do valor
                            </Text>
                        </View>
                    </View>
                </View>

                {/* Termos */}
                <Text className="text-xs text-gray-400 text-center mt-6 px-4">
                    Ao confirmar, você concorda com os Termos de Uso e Política de Privacidade do GoDrive.
                </Text>

                {/* Espaço para o botão fixo */}
                <View className="h-28" />
            </ScrollView>

            {/* Botão Fixo - Confirmar */}
            <View className="absolute bottom-0 left-0 right-0 px-6 pb-8 pt-4 bg-white border-t border-gray-100">
                <TouchableOpacity
                    onPress={handleConfirm}
                    disabled={isSubmitting}
                    className={`py-4 rounded-xl items-center flex-row justify-center ${isSubmitting ? 'bg-neutral-200' : 'bg-primary-600 active:bg-primary-700'
                        }`}
                    accessibilityLabel="Confirmar Agendamento"
                >
                    {isSubmitting ? (
                        <>
                            <ActivityIndicator size="small" color="#6B7280" />
                            <Text className="text-base font-semibold text-neutral-400 ml-2">
                                Processando...
                            </Text>
                        </>
                    ) : (
                        <Text className="text-base font-semibold text-white">
                            Confirmar Agendamento
                        </Text>
                    )}
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
