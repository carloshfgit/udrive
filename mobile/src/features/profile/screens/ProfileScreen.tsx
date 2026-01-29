import React, { useEffect } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useAuthStore } from '../../../lib/store';

export function ProfileScreen() {
    const { user, logout } = useAuthStore();

    return (
        <View className="flex-1 items-center justify-center bg-white p-4">
            <Text className="text-2xl font-bold text-blue-600 mb-4">Perfil</Text>
            {user && (
                <View className="mb-8 items-center">
                    <Text className="text-lg font-semibold text-gray-800">{user.full_name}</Text>
                    <Text className="text-gray-600">{user.email}</Text>
                    <Text className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold mt-2 uppercase">
                        {user.type}
                    </Text>
                </View>
            )}

            <TouchableOpacity
                className="bg-red-500 px-6 py-3 rounded-xl active:bg-red-600"
                onPress={() => logout()}
            >
                <Text className="text-white font-semibold">Sair da Conta</Text>
            </TouchableOpacity>
        </View>
    );
}
