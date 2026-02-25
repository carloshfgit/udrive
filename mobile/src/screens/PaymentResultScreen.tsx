/**
 * PaymentResultScreen
 * 
 * Tela exibida após retorno do Checkout Pro via deep link.
 * Recebe o parâmetro `status` da rota (success, error, pending).
 */

import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation, useRoute, type RouteProp } from '@react-navigation/native';
import { useQueryClient } from '@tanstack/react-query';
import { CheckCircle, XCircle, Clock } from 'lucide-react-native';
import { CART_ITEMS_QUERY_KEY } from '../features/shared-features/scheduling/hooks/usePayment';

type PaymentResultParams = {
    PaymentResult: { status: 'success' | 'error' | 'pending' };
};

const configs = {
    success: {
        icon: CheckCircle,
        iconColor: '#16A34A',
        title: 'Pagamento Confirmado!',
        message: 'Suas aulas foram confirmadas com sucesso. O instrutor será notificado.',
        buttonText: 'Ver Minhas Aulas',
        bgColor: '#F0FDF4',
    },
    error: {
        icon: XCircle,
        iconColor: '#DC2626',
        title: 'Pagamento não realizado',
        message: 'Houve um problema com o pagamento. Tente novamente ou entre em contato com o suporte.',
        buttonText: 'Tentar Novamente',
        bgColor: '#FEF2F2',
    },
    pending: {
        icon: Clock,
        iconColor: '#D97706',
        title: 'Pagamento em Processamento',
        message: 'Seu pagamento está sendo processado. Você receberá uma notificação quando for confirmado.',
        buttonText: 'Voltar',
        bgColor: '#FFFBEB',
    },
} as const;

export function PaymentResultScreen() {
    const navigation = useNavigation();
    const route = useRoute<RouteProp<PaymentResultParams, 'PaymentResult'>>();
    const queryClient = useQueryClient();

    const status = route.params?.status ?? 'pending';
    const config = configs[status] ?? configs.pending;
    const IconComponent = config.icon;

    // Invalidar caches ao montar
    useEffect(() => {
        queryClient.invalidateQueries({ queryKey: CART_ITEMS_QUERY_KEY });
        queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
    }, [queryClient]);

    const handlePress = () => {
        // Navega para a tela de Minhas Aulas dentro do Tab Navigator (Scheduling > MyLessons)
        navigation.reset({
            index: 0,
            routes: [
                {
                    name: 'Main' as never,
                    params: {
                        screen: 'Scheduling',
                        params: { screen: 'MyLessons' },
                    },
                } as never,
            ],
        });
    };

    return (
        <SafeAreaView style={[styles.container, { backgroundColor: config.bgColor }]}>
            <View style={styles.content}>
                <IconComponent color={config.iconColor} size={80} strokeWidth={1.5} />
                <Text style={[styles.title, { color: config.iconColor }]}>{config.title}</Text>
                <Text style={styles.message}>{config.message}</Text>
            </View>

            <TouchableOpacity
                style={[styles.button, { backgroundColor: config.iconColor }]}
                onPress={handlePress}
                activeOpacity={0.8}
            >
                <Text style={styles.buttonText}>{config.buttonText}</Text>
            </TouchableOpacity>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'space-between',
        paddingHorizontal: 24,
        paddingVertical: 40,
    },
    content: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16,
    },
    title: {
        fontSize: 24,
        fontWeight: '700',
        textAlign: 'center',
        marginTop: 16,
    },
    message: {
        fontSize: 16,
        color: '#4B5563',
        textAlign: 'center',
        lineHeight: 24,
        paddingHorizontal: 16,
    },
    button: {
        paddingVertical: 16,
        borderRadius: 12,
        alignItems: 'center',
    },
    buttonText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '600',
    },
});
