/**
 * ProfileScreen
 *
 * Tela principal do perfil do aluno seguindo referência visual.
 */

import React from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import {
    User,
    Calendar,
    History,
    CreditCard,
    Settings,
    LogOut,
    ChevronRight,
    Camera,
    Edit3,
} from 'lucide-react-native';

import { useAuthStore } from '../../../../lib/store';
import { Avatar, Badge } from '../../../../shared/components';
import { ProfileStackParamList } from '../navigation/ProfileStackNavigator';

type ProfileNavigationProp = NativeStackNavigationProp<ProfileStackParamList, 'ProfileMain'>;

// Versão do app
const APP_VERSION = '2.4.0';

// Itens do menu de perfil
const MENU_ITEMS = [
    {
        id: 'personal',
        title: 'Informações Pessoais',
        icon: User,
        route: 'PersonalInfo' as const,
    },
    {
        id: 'bookings',
        title: 'Meus Agendamentos',
        icon: Calendar,
        route: null, // TODO: Implementar
    },
    {
        id: 'history',
        title: 'Histórico de Aulas',
        icon: History,
        route: null, // TODO: Implementar
    },
    {
        id: 'payments',
        title: 'Pagamentos',
        icon: CreditCard,
        route: null, // TODO: Implementar
    },
    {
        id: 'settings',
        title: 'Configurações',
        icon: Settings,
        route: null, // TODO: Implementar
    },
];

export function ProfileScreen() {
    const navigation = useNavigation<ProfileNavigationProp>();
    const { user, logout } = useAuthStore();

    const handleMenuItemPress = (route: string | null) => {
        if (route === 'PersonalInfo') {
            navigation.navigate('PersonalInfo');
        }
        // TODO: Implementar outras rotas
    };

    const handleEditPhoto = () => {
        // TODO: Implementar expo-image-picker
        console.log('Edit photo pressed');
    };

    const handleLogout = () => {
        logout();
    };

    // Extrair iniciais do nome para fallback do avatar
    const getInitials = (name?: string) => {
        if (!name) return '?';
        return name
            .split(' ')
            .map((n) => n[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="flex-row items-center justify-between px-4 py-3">
                <View className="w-10" />
                <Text className="text-lg font-bold text-gray-900">Perfil do Aluno</Text>
                <TouchableOpacity
                    className="w-10 items-end"
                    accessibilityLabel="Editar perfil"
                >
                    <Edit3 size={20} color="#111318" />
                </TouchableOpacity>
            </View>

            <ScrollView
                className="flex-1"
                contentContainerClassName="pb-8"
                showsVerticalScrollIndicator={false}
            >
                {/* Avatar Section */}
                <View className="items-center py-6">
                    <View className="relative">
                        <View className="w-32 h-32 rounded-full border-4 border-blue-100 overflow-hidden bg-gray-200 items-center justify-center">
                            {user?.avatarUrl ? (
                                <Avatar
                                    source={user.avatarUrl}
                                    size="xl"
                                    className="w-full h-full"
                                />
                            ) : (
                                <Text className="text-3xl font-bold text-gray-500">
                                    {getInitials(user?.full_name)}
                                </Text>
                            )}
                        </View>
                        {/* Camera Badge */}
                        <TouchableOpacity
                            onPress={handleEditPhoto}
                            className="absolute bottom-1 right-1 bg-blue-600 p-2 rounded-full border-2 border-white"
                            accessibilityLabel="Alterar foto de perfil"
                        >
                            <Camera size={14} color="#ffffff" />
                        </TouchableOpacity>
                    </View>

                    {/* Nome */}
                    <Text className="text-xl font-bold text-gray-900 mt-4">
                        {user?.full_name || 'Nome do Aluno'}
                    </Text>

                    {/* Badge de Categoria */}
                    <View className="mt-2 px-3 py-1 bg-blue-50 rounded-full">
                        <Text className="text-sm font-semibold text-blue-600">
                            Categoria B
                        </Text>
                    </View>
                </View>

                {/* Menu Items */}
                <View className="px-2 mt-4">
                    {MENU_ITEMS.map((item) => {
                        const IconComponent = item.icon;
                        return (
                            <TouchableOpacity
                                key={item.id}
                                onPress={() => handleMenuItemPress(item.route)}
                                className="flex-row items-center px-4 py-4 rounded-xl active:bg-gray-50"
                                accessibilityLabel={item.title}
                            >
                                {/* Icon Container */}
                                <View className="w-10 h-10 rounded-lg bg-blue-50 items-center justify-center">
                                    <IconComponent size={20} color="#2563EB" />
                                </View>

                                {/* Title */}
                                <Text className="flex-1 ml-4 text-base font-medium text-gray-900">
                                    {item.title}
                                </Text>

                                {/* Chevron */}
                                <ChevronRight size={20} color="#9CA3AF" />
                            </TouchableOpacity>
                        );
                    })}
                </View>
            </ScrollView>

            {/* Footer with Logout and Version */}
            <View className="px-6 pb-8 pt-4">
                <TouchableOpacity
                    onPress={handleLogout}
                    className="flex-row items-center justify-center py-4 rounded-xl border border-red-100 bg-red-50 active:bg-red-100"
                    accessibilityLabel="Sair da conta"
                >
                    <LogOut size={20} color="#DC2626" />
                    <Text className="ml-2 text-base font-semibold text-red-600">
                        Sair da Conta
                    </Text>
                </TouchableOpacity>

                <Text className="text-center text-xs text-gray-400 mt-6 opacity-60">
                    Versão {APP_VERSION} • GoDrive
                </Text>
            </View>
        </SafeAreaView>
    );
}
