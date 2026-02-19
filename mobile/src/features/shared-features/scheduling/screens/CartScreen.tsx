/**
 * GoDrive Mobile - CartScreen
 *
 * Tela de carrinho exibindo aulas pendentes de pagamento.
 * Permite o checkout multi-item via Mercado Pago Checkout Pro.
 * Inclui remoção de itens individuais e timer de expiração de 12 minutos.
 */

import React, { useMemo, useCallback, useState, useEffect, useRef } from 'react';
import {
    View,
    Text,
    FlatList,
    TouchableOpacity,
    SafeAreaView,
    RefreshControl,
    Alert,
    ActivityIndicator,
    Animated,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { ChevronLeft, ShoppingCart, Calendar, Clock, CreditCard, Trash2, AlertTriangle } from 'lucide-react-native';
import * as WebBrowser from 'expo-web-browser';

import { useAuthStore } from '../../../../lib/store';
import { Badge } from '../../../../shared/components/Badge';
import { EmptyState } from '../../../../shared/components/EmptyState';
import { LoadingState } from '../../../../shared/components/LoadingState';
import { Avatar } from '../../../../shared/components/Avatar';
import { formatPrice } from '../../../../shared';
import { useCartItems, useCreateCheckout, useRemoveCartItem, useClearStudentCart, CART_ITEMS_QUERY_KEY } from '../hooks/usePayment';
import { BookingResponse } from '../api/schedulingApi';

// ============= Constants =============

const CART_TIMEOUT_MINUTES = 12;
const CART_TIMEOUT_MS = CART_TIMEOUT_MINUTES * 60 * 1000;
const WARNING_THRESHOLD_SECONDS = 120; // Aviso visual a 2 minutos do fim

// ============= Helpers =============

const WEEK_DAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
const MONTHS = [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez',
];



function formatDate(isoString: string): string {
    const d = new Date(isoString);
    return `${WEEK_DAYS[d.getDay()]}, ${d.getDate()} ${MONTHS[d.getMonth()]}`;
}

function formatTime(isoString: string): string {
    const d = new Date(isoString);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
}

function formatCountdown(seconds: number): string {
    if (seconds <= 0) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// ============= Cart Timer Hook =============

function useCartTimer(cartItems: BookingResponse[], serverExpiresAt?: string | null) {
    const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

    useEffect(() => {
        if (cartItems.length === 0) {
            setTimeRemaining(null);
            return;
        }

        let expiresAt: number;

        if (serverExpiresAt) {
            // P3: Usar timestamp do servidor como source-of-truth
            expiresAt = new Date(serverExpiresAt).getTime();
        } else {
            // Fallback: cálculo local (compatibilidade)
            const oldestCreatedAt = cartItems.reduce((oldest, item) => {
                const createdAt = new Date(item.created_at).getTime();
                return createdAt < oldest ? createdAt : oldest;
            }, Infinity);
            expiresAt = oldestCreatedAt + CART_TIMEOUT_MS;
        }

        const updateTimer = () => {
            const remaining = Math.max(0, Math.floor((expiresAt - Date.now()) / 1000));
            setTimeRemaining(remaining);
        };

        updateTimer();
        const interval = setInterval(updateTimer, 1000);

        return () => clearInterval(interval);
    }, [cartItems, serverExpiresAt]);

    const isExpiring = timeRemaining !== null && timeRemaining <= WARNING_THRESHOLD_SECONDS && timeRemaining > 0;
    const isExpired = timeRemaining !== null && timeRemaining <= 0;

    return {
        timeRemaining,
        formattedTime: timeRemaining !== null ? formatCountdown(timeRemaining) : null,
        isExpiring,
        isExpired,
    };
}

// ============= Cart Item Component =============

function CartItemCard({
    item,
    onRemove,
    isRemoving,
}: {
    item: BookingResponse;
    onRemove: (id: string) => void;
    isRemoving: boolean;
}) {
    const scheduledDate = new Date(item.scheduled_datetime);

    const handleRemove = () => {
        Alert.alert(
            'Remover do Carrinho',
            `Deseja remover esta aula?\n\nO agendamento será cancelado e o horário do instrutor será liberado.`,
            [
                { text: 'Cancelar', style: 'cancel' },
                {
                    text: 'Remover',
                    style: 'destructive',
                    onPress: () => onRemove(item.id),
                },
            ]
        );
    };

    return (
        <View className="bg-white rounded-2xl p-4 mb-3 border border-neutral-100 shadow-sm">
            <View className="flex-row items-center">
                {/* Date block */}
                <View className="bg-primary-50 px-3 py-2 rounded-xl items-center justify-center mr-3 min-w-[60px]">
                    <Text className="text-primary-700 font-black text-xl leading-none">
                        {scheduledDate.getDate()}
                    </Text>
                    <Text className="text-primary-500 text-[9px] font-bold uppercase tracking-widest mt-0.5">
                        {MONTHS[scheduledDate.getMonth()]}
                    </Text>
                </View>

                {/* Info */}
                <View className="flex-1">
                    <Text className="text-neutral-800 font-semibold text-base" numberOfLines={1}>
                        {item.instructor_name || 'Instrutor'}
                    </Text>
                    <View className="flex-row items-center mt-1">
                        <Clock size={12} color="#9CA3AF" />
                        <Text className="text-neutral-500 text-sm ml-1">
                            {formatTime(item.scheduled_datetime)} • {item.duration_minutes}min
                        </Text>
                    </View>
                </View>

                {/* Price */}
                <Text className="text-neutral-900 font-bold text-base mr-2">
                    {formatPrice(item.price)}
                </Text>

                {/* Remove Button */}
                <TouchableOpacity
                    onPress={handleRemove}
                    disabled={isRemoving}
                    className="w-9 h-9 items-center justify-center rounded-lg bg-red-50 active:bg-red-100"
                    accessibilityLabel={`Remover aula de ${item.instructor_name || 'instrutor'} do carrinho`}
                >
                    {isRemoving ? (
                        <ActivityIndicator size="small" color="#EF4444" />
                    ) : (
                        <Trash2 size={16} color="#EF4444" />
                    )}
                </TouchableOpacity>
            </View>
        </View>
    );
}

// ============= Timer Banner Component =============

function TimerBanner({
    formattedTime,
    isExpiring,
}: {
    formattedTime: string;
    isExpiring: boolean;
}) {
    const pulseAnim = useRef(new Animated.Value(1)).current;

    useEffect(() => {
        if (isExpiring) {
            const pulse = Animated.loop(
                Animated.sequence([
                    Animated.timing(pulseAnim, {
                        toValue: 0.6,
                        duration: 600,
                        useNativeDriver: true,
                    }),
                    Animated.timing(pulseAnim, {
                        toValue: 1,
                        duration: 600,
                        useNativeDriver: true,
                    }),
                ])
            );
            pulse.start();
            return () => pulse.stop();
        } else {
            pulseAnim.setValue(1);
        }
    }, [isExpiring]);

    return (
        <Animated.View
            style={{ opacity: isExpiring ? pulseAnim : 1 }}
            className={`flex-row items-center justify-center py-2.5 px-4 rounded-xl mb-3 ${isExpiring ? 'bg-red-50 border border-red-200' : 'bg-amber-50 border border-amber-200'
                }`}
        >
            {isExpiring ? (
                <AlertTriangle size={16} color="#EF4444" />
            ) : (
                <Clock size={16} color="#D97706" />
            )}
            <Text
                className={`ml-2 font-bold text-sm ${isExpiring ? 'text-red-600' : 'text-amber-700'
                    }`}
            >
                {isExpiring ? 'Carrinho expirando! ' : 'Tempo restante: '}
            </Text>
            <Text
                className={`font-black text-base tabular-nums ${isExpiring ? 'text-red-700' : 'text-amber-800'
                    }`}
            >
                {formattedTime}
            </Text>
        </Animated.View>
    );
}

// ============= Main Screen =============

export function CartScreen() {
    const navigation = useNavigation<any>();
    const { user } = useAuthStore();
    const { data, isLoading, refetch, isRefetching } = useCartItems();
    const createCheckoutMutation = useCreateCheckout();
    const removeCartItemMutation = useRemoveCartItem();
    const clearCartMutation = useClearStudentCart();
    const wasExpired = useRef(false);

    // Refresh on focus
    useFocusEffect(
        useCallback(() => {
            refetch();
        }, [refetch])
    );

    const cartItems = useMemo(() => data?.schedulings ?? [], [data?.schedulings]);

    // Cart timer — usa cart_expires_at do servidor (P3)
    const serverExpiresAt = data?.cart_expires_at ?? null;
    const { formattedTime, isExpiring, isExpired } = useCartTimer(cartItems, serverExpiresAt);

    // Auto-refresh when expired
    useEffect(() => {
        if (isExpired && cartItems.length > 0 && !wasExpired.current && !clearCartMutation.isPending) {
            wasExpired.current = true;
            clearCartMutation.mutate(undefined, {
                onSuccess: () => {
                    Alert.alert(
                        'Tempo Expirado',
                        'Seu tempo para finalizar o pagamento acabou. Os horários foram liberados.',
                        [{ text: 'OK', onPress: () => refetch() }]
                    );
                },
                onError: () => {
                    // Se falhar, permite tentar de novo no próximo tick se ainda estiver expirado
                    wasExpired.current = false;
                }
            });
        }

        // Reset a trava se o carrinho ficar vazio (por exemplo, após a limpeza)
        if (cartItems.length === 0) {
            wasExpired.current = false;
        }
    }, [isExpired, cartItems.length, clearCartMutation, refetch]);

    const totalPrice = useMemo(
        () => cartItems.reduce((sum, item) => {
            const price = typeof item.price === 'string' ? parseFloat(item.price) : item.price;
            return sum + (isNaN(price) ? 0 : price);
        }, 0),
        [cartItems]
    );

    const instructorName = cartItems.length > 0
        ? (cartItems[0].instructor_name || 'Instrutor')
        : '';

    const handleRemoveItem = (schedulingId: string) => {
        removeCartItemMutation.mutate(schedulingId);
    };

    const handleCheckout = async () => {
        if (cartItems.length === 0 || !user) return;

        try {
            const result = await createCheckoutMutation.mutateAsync({
                scheduling_ids: cartItems.map((item) => item.id),
                student_id: user.id,
                student_email: user.email,
            });

            // Abre o Checkout Pro no browser in-app
            await WebBrowser.openBrowserAsync(result.checkout_url);
        } catch (error: any) {
            const message =
                error?.response?.data?.detail ||
                'Erro ao criar checkout. Tente novamente.';
            Alert.alert('Erro', message);
        }
    };

    const isCheckingOut = createCheckoutMutation.isPending;

    return (
        <SafeAreaView className="flex-1 bg-neutral-50">
            {/* Header */}
            <View className="flex-row items-center px-4 py-3 border-b border-neutral-100 bg-white">
                <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    className="w-10 h-10 items-center justify-center"
                    accessibilityLabel="Voltar"
                >
                    <ChevronLeft size={24} color="#111318" />
                </TouchableOpacity>
                <Text className="flex-1 text-lg font-bold text-gray-900 text-center">
                    Carrinho
                </Text>
                <View className="w-10" />
            </View>

            {/* Content */}
            <FlatList
                data={cartItems}
                renderItem={({ item }) => (
                    <CartItemCard
                        item={item}
                        onRemove={handleRemoveItem}
                        isRemoving={
                            removeCartItemMutation.isPending &&
                            removeCartItemMutation.variables === item.id
                        }
                    />
                )}
                keyExtractor={(item) => item.id}
                contentContainerStyle={{ padding: 16, paddingBottom: 200 }}
                showsVerticalScrollIndicator={false}
                refreshControl={
                    <RefreshControl
                        refreshing={isRefetching}
                        onRefresh={refetch}
                        colors={['#2563EB']}
                    />
                }
                ListHeaderComponent={
                    cartItems.length > 0 ? (
                        <View className="mb-1">
                            {/* Timer Banner */}
                            {formattedTime && (
                                <TimerBanner
                                    formattedTime={formattedTime}
                                    isExpiring={isExpiring}
                                />
                            )}
                            <Text className="text-neutral-500 text-sm font-medium mb-2">
                                {cartItems.length} {cartItems.length === 1 ? 'aula' : 'aulas'} com {instructorName}
                            </Text>
                        </View>
                    ) : null
                }
                ListEmptyComponent={
                    isLoading ? (
                        <View>
                            <LoadingState.Card />
                            <LoadingState.Card />
                        </View>
                    ) : (
                        <EmptyState
                            icon={<ShoppingCart size={32} color="#2563EB" />}
                            title="Carrinho vazio"
                            message="Você não possui aulas aguardando pagamento no momento."
                        />
                    )
                }
            />

            {/* Bottom Summary + Checkout Button */}
            {cartItems.length > 0 && (
                <View className="absolute bottom-0 left-0 right-0 bg-white border-t border-neutral-100 px-6 pb-8 pt-4 shadow-lg">
                    {/* Summary */}
                    <View className="flex-row justify-between items-center mb-4">
                        <View>
                            <Text className="text-neutral-500 text-sm">Total</Text>
                            <Text className="text-neutral-900 font-black text-2xl">
                                {formatPrice(totalPrice)}
                            </Text>
                        </View>
                        <Badge
                            label={`${cartItems.length} ${cartItems.length === 1 ? 'aula' : 'aulas'}`}
                            variant="default"
                        />
                    </View>

                    {/* Checkout Button */}
                    <TouchableOpacity
                        onPress={handleCheckout}
                        disabled={isCheckingOut || isExpired}
                        className={`py-4 rounded-xl items-center flex-row justify-center ${isCheckingOut || isExpired
                            ? 'bg-neutral-200'
                            : 'bg-primary-600 active:bg-primary-700'
                            }`}
                        accessibilityLabel="Finalizar Pagamento"
                    >
                        {isCheckingOut ? (
                            <>
                                <ActivityIndicator size="small" color="#6B7280" />
                                <Text className="text-base font-semibold text-neutral-400 ml-2">
                                    Processando...
                                </Text>
                            </>
                        ) : isExpired ? (
                            <>
                                <AlertTriangle size={20} color="#6B7280" />
                                <Text className="text-base font-semibold text-neutral-400 ml-2">
                                    Carrinho Expirado
                                </Text>
                            </>
                        ) : (
                            <>
                                <CreditCard size={20} color="#FFFFFF" />
                                <Text className="text-base font-semibold text-white ml-2">
                                    Finalizar Pagamento
                                </Text>
                            </>
                        )}
                    </TouchableOpacity>
                </View>
            )}
        </SafeAreaView>
    );
}
