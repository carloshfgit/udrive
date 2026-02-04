/**
 * GoDrive Mobile - BookingSuccessScreen
 *
 * Tela de sucesso após criação do agendamento.
 */

import React from 'react';
import {
    View,
    Text,
    TouchableOpacity,
    SafeAreaView,
} from 'react-native';
import { useNavigation, useRoute, RouteProp, CommonActions } from '@react-navigation/native';
import { CheckCircle, Calendar, ArrowRight } from 'lucide-react-native';

import { SchedulingStackParamList } from './SelectDateTimeScreen';

type BookingSuccessRouteProp = RouteProp<SchedulingStackParamList, 'BookingSuccess'>;

// Formatador de data
const formatDateTimeBR = (isoString: string): string => {
    const date = new Date(isoString);
    const options: Intl.DateTimeFormatOptions = {
        weekday: 'short',
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    };
    return date.toLocaleDateString('pt-BR', options).replace(',', ' às');
};

export function BookingSuccessScreen() {
    const navigation = useNavigation();
    const route = useRoute<BookingSuccessRouteProp>();
    const { instructorName, scheduledDatetime } = route.params;

    const formattedDateTime = formatDateTimeBR(scheduledDatetime);

    // Navegar para Meus Agendamentos
    const handleViewSchedulings = () => {
        // Reset stack e ir para a tab de Aulas
        navigation.dispatch(
            CommonActions.reset({
                index: 0,
                routes: [
                    {
                        name: 'Main',
                        state: {
                            routes: [{ name: 'Scheduling' }],
                            index: 0,
                        },
                    },
                ],
            })
        );
    };

    // Voltar para a Home
    const handleGoHome = () => {
        // Reset stack e ir para Home
        navigation.dispatch(
            CommonActions.reset({
                index: 0,
                routes: [
                    {
                        name: 'Main',
                        state: {
                            routes: [{ name: 'Home' }],
                            index: 0,
                        },
                    },
                ],
            })
        );
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            <View className="flex-1 items-center justify-center px-8">
                {/* Ícone de Sucesso */}
                <View className="w-24 h-24 rounded-full bg-success-100 items-center justify-center mb-6">
                    <CheckCircle size={48} color="#16A34A" />
                </View>

                {/* Título */}
                <Text className="text-2xl font-bold text-gray-900 text-center">
                    Aula Agendada!
                </Text>

                {/* Subtítulo */}
                <Text className="text-base text-gray-500 text-center mt-2">
                    Seu agendamento foi enviado para o instrutor e aguarda confirmação.
                </Text>

                {/* Card de Info */}
                <View className="mt-8 w-full bg-neutral-50 rounded-2xl p-4 border border-neutral-100">
                    <View className="flex-row items-center">
                        <View className="w-12 h-12 rounded-full bg-primary-100 items-center justify-center">
                            <Calendar size={24} color="#2563EB" />
                        </View>
                        <View className="flex-1 ml-3">
                            <Text className="text-sm text-gray-500">
                                Aula com {instructorName}
                            </Text>
                            <Text className="text-base font-semibold text-gray-900 capitalize">
                                {formattedDateTime}
                            </Text>
                        </View>
                    </View>
                </View>

                {/* Aviso */}
                <Text className="text-sm text-gray-400 text-center mt-6 px-4">
                    Você receberá uma notificação quando o instrutor confirmar a aula.
                </Text>
            </View>

            {/* Botões */}
            <View className="px-6 pb-8">
                <TouchableOpacity
                    onPress={handleViewSchedulings}
                    className="py-4 rounded-xl items-center bg-primary-600 active:bg-primary-700 flex-row justify-center"
                    accessibilityLabel="Ver Meus Agendamentos"
                >
                    <Text className="text-base font-semibold text-white">
                        Ver Meus Agendamentos
                    </Text>
                    <ArrowRight size={18} color="#FFFFFF" className="ml-2" />
                </TouchableOpacity>

                <TouchableOpacity
                    onPress={handleGoHome}
                    className="py-4 mt-3 rounded-xl items-center bg-transparent border border-neutral-200 active:bg-neutral-50"
                    accessibilityLabel="Voltar ao Início"
                >
                    <Text className="text-base font-semibold text-gray-700">
                        Voltar ao Início
                    </Text>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
