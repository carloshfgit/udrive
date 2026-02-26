/**
 * LinkMercadoPagoScreen
 *
 * Tela para o instrutor vincular sua conta Mercado Pago via OAuth.
 * Exibe informações sobre o processo e botão para iniciar a vinculação.
 */

import React, { useCallback, useState, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
    ActivityIndicator,
    Alert,
    Image,
    AppState,
    AppStateStatus,
} from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import {
    ArrowLeft,
    Shield,
    Zap,
    Banknote,
    Smartphone,
    CheckCircle2,
    ExternalLink,
} from 'lucide-react-native';

import { useInstructorProfile } from '../hooks/useInstructorProfile';
import { getOAuthAuthorizeUrl } from '../api/paymentApi';

const MP_LOGO_FULL = require('../../../../assets/images/logo-mercado-pago-1024.png');
const MP_ICON = require('../../../../assets/images/logo-mercado-pago-icone-512.png');

// Cards informativos para o instrutor
const INFO_CARDS = [
    {
        id: 'security',
        icon: Shield,
        emoji: '🔒',
        text: `• Para a segurança dos nossos usuários, selecionamos o Mercado Pago como nossa plataforma oficial de pagamentos.
• Todo o processo é feito pelo Mercado Pago, não armazenamos nenhum dado sensível de pagamento.`,
        color: '#059669',
        bgColor: '#ECFDF5',
    },
    {
        id: 'value',
        icon: Banknote,
        emoji: '💰',
        text: `• Você recebe o valor integral que definiu, sem descontos, sem taxas.
• O aluno paga pelo app e você recebe diretamente na sua conta do Mercado Pago.`,
        color: '#2563EB',
        bgColor: '#EFF6FF',
    },
    {
        id: 'quick',
        icon: Smartphone,
        emoji: '📱',
        text: '• A vinculação é feita uma única vez e leva menos de 1 minuto.',
        color: '#7C3AED',
        bgColor: '#F5F3FF',
    },
];

export function LinkMercadoPagoScreen() {
    const navigation = useNavigation();
    const { data: profile, refetch } = useInstructorProfile();
    const [isLoading, setIsLoading] = useState(false);

    // Refetch the profile when the screen comes into focus
    useFocusEffect(
        useCallback(() => {
            if (refetch) {
                refetch();
            }
        }, [refetch])
    );

    // Refetch the profile when the app returns from background/web browser
    useEffect(() => {
        const subscription = AppState.addEventListener('change', (nextAppState: AppStateStatus) => {
            if (nextAppState === 'active' && refetch) {
                refetch();
            }
        });

        return () => {
            subscription.remove();
        };
    }, [refetch]);

    // Verifica se a conta MP já está vinculada
    // O campo has_mp_account pode não existir ainda no backend (Etapa 1)
    const isConnected = !!(profile as any)?.has_mp_account;

    const handleLinkAccount = useCallback(async () => {
        setIsLoading(true);
        try {
            // Geramos a URL de retorno dinâmica (compatível com Expo Go e Produção)
            const returnUrl = Linking.createURL('oauth/callback');

            const { authorization_url } = await getOAuthAuthorizeUrl(returnUrl);

            // Usamos openAuthSessionAsync que captura o Deep Link e fecha o browser automaticamente
            const result = await WebBrowser.openAuthSessionAsync(authorization_url, returnUrl);

            // Se o login foi concluído com sucesso, o browser fecha e caímos aqui
            if (result.type === 'success' && refetch) {
                refetch();
            }
        } catch (error: unknown) {
            const message =
                error instanceof Error
                    ? error.message
                    : 'Não foi possível iniciar a vinculação.';
            Alert.alert('Erro', message);
        } finally {
            setIsLoading(false);
        }
    }, [refetch]);

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
                <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    className="w-10 h-10 items-center justify-center rounded-full active:bg-gray-100"
                    accessibilityLabel="Voltar"
                >
                    <ArrowLeft size={22} color="#1F2937" />
                </TouchableOpacity>
                <Text className="flex-1 text-lg font-bold text-gray-900 text-center mr-10">
                    Mercado Pago
                </Text>
            </View>

            <ScrollView
                className="flex-1"
                contentContainerClassName="px-5 py-6 pb-10"
                showsVerticalScrollIndicator={false}
            >
                {/* Logo / Ícone */}
                <View className="items-center mb-6">
                    <View className="w-full h-32 items-center justify-center mb-2">
                        <Image
                            source={MP_LOGO_FULL}
                            className="w-128 h-64"
                            resizeMode="contain"
                        />
                    </View>
                    <Text className="text-2xl font-bold text-gray-900 text-center">
                        Vincule sua conta{'\n'}Mercado Pago
                    </Text>
                    <Text className="text-sm text-gray-500 mt-2 text-center">
                        Receba seus pagamentos de forma rápida e segura.
                    </Text>
                </View>

                {/* Status de conexão */}
                {isConnected && (
                    <View className="flex-row items-center bg-green-50 px-4 py-3 rounded-xl mb-6 border border-green-200">
                        <CheckCircle2 size={22} color="#059669" />
                        <Text className="flex-1 ml-3 text-sm font-semibold text-green-700">
                            Conta Mercado Pago vinculada
                        </Text>
                    </View>
                )}

                {/* Cards informativos */}
                <View className="gap-3 mb-8">
                    {INFO_CARDS.map((card) => (
                        <View
                            key={card.id}
                            className="flex-row items-start p-4 rounded-xl"
                            style={{ backgroundColor: card.bgColor }}
                        >
                            <Text className="text-xl mr-3 mt-0.5">{card.emoji}</Text>
                            <Text
                                className="flex-1 text-sm leading-5"
                                style={{ color: card.color }}
                            >
                                {card.text}
                            </Text>
                        </View>
                    ))}
                </View>

                {/* Seção de como funciona */}
                <View className="bg-gray-50 p-4 rounded-xl mb-8">
                    <Text className="text-sm font-semibold text-gray-700 mb-2">
                        Como funciona?
                    </Text>
                    <Text className="text-xs text-gray-500 leading-5">
                        Ao clicar no botão abaixo, você será redirecionado para o site oficial
                        do Mercado Pago para vincular sua conta. Todo o processo é seguro e leva menos de 1 minuto.
                        Caso não tenha uma conta no Mercado Pago, você poderá criar uma.
                    </Text>
                </View>
            </ScrollView>

            {/* Footer com botão */}
            <View className="px-5 pb-8 pt-4 border-t border-gray-100">
                {!isConnected ? (
                    <TouchableOpacity
                        onPress={handleLinkAccount}
                        disabled={isLoading}
                        className="flex-row items-center justify-center py-4 rounded-xl bg-[#00AEEF] active:opacity-80"
                        accessibilityLabel="Vincular conta Mercado Pago"
                    >
                        {isLoading ? (
                            <ActivityIndicator color="#ffffffff" />
                        ) : (
                            <>
                                <Image
                                    source={MP_ICON}
                                    className="w-10 h-10 mr-2"
                                    resizeMode="contain"
                                />
                                <Text className="ml-2 text-base font-bold text-white">
                                    Vincular conta Mercado Pago
                                </Text>
                            </>
                        )}
                    </TouchableOpacity>
                ) : (
                    <View className="items-center py-4">
                        <Text className="text-sm text-gray-500">
                            Sua conta já está vinculada ✅
                        </Text>
                    </View>
                )}
            </View>
        </SafeAreaView>
    );
}
