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
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useQueryClient } from '@tanstack/react-query';
import { CheckCircle, Calendar, ArrowRight, ShoppingCart } from 'lucide-react-native';

import { SchedulingStackParamList } from './SelectDateTimeScreen';
import { CART_ITEMS_QUERY_KEY } from '../hooks/usePayment';

type BookingSuccessRouteProp = RouteProp<SchedulingStackParamList, 'BookingSuccess'>;
type BookingSuccessNavigationProp = NativeStackNavigationProp<SchedulingStackParamList, 'BookingSuccess'>;

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
    const navigation = useNavigation<BookingSuccessNavigationProp>();
    const route = useRoute<BookingSuccessRouteProp>();
    const {
        instructorName,
        scheduledDatetime,
        instructorId,
        instructorAvatar,
        hourlyRate,
        licenseCategory,
        rating
    } = route.params;

    const queryClient = useQueryClient();

    const formattedDateTime = formatDateTimeBR(scheduledDatetime);

    // Navegar para o Carrinho
    const handleViewCart = () => {
        // Invalida o cache para garantir que a lista seja atualizada
        queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
        queryClient.invalidateQueries({ queryKey: CART_ITEMS_QUERY_KEY });

        // Navega para a aba de "Aulas" (Scheduling) e para a tela de "Carrinho" (Cart)
        // Isso garante que funcione tanto se o usuário iniciou o agendamento pela Busca 
        // quanto pela tela de Aulas.
        navigation.navigate('Scheduling' as any, {
            screen: 'Cart',
        });
    };

    // Agendar mais uma aula com o mesmo instrutor
    const handleScheduleAnother = () => {
        navigation.navigate('SelectDateTime', {
            instructorId,
            instructorName,
            instructorAvatar,
            hourlyRate,
            licenseCategory,
            rating,
        });
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
                    Seu agendamento foi adicionado ao carrinho e aguarda o pagamento para ser confirmado na sua agenda.
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
                    onPress={handleViewCart}
                    className="py-4 rounded-xl items-center bg-primary-600 active:bg-primary-700 flex-row justify-center"
                    accessibilityLabel="Ver Carrinho"
                >
                    <ShoppingCart size={18} color="#FFFFFF" />
                    <Text className="text-base font-semibold text-white ml-2">
                        Ver Carrinho
                    </Text>
                </TouchableOpacity>

                <TouchableOpacity
                    onPress={handleScheduleAnother}
                    className="py-4 mt-3 rounded-xl items-center bg-transparent border border-neutral-200 active:bg-neutral-50"
                    accessibilityLabel="Agendar mais uma aula"
                >
                    <Text className="text-base font-semibold text-gray-700">
                        Agendar mais uma aula
                    </Text>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
