import React from 'react';
import { View, Text } from 'react-native';

export function HomeScreen() {
    return (
        <View className="flex-1 items-center justify-center bg-white">
            <Text className="text-2xl font-bold text-blue-600">Início</Text>
            <Text className="text-gray-500 mt-2">Em breve: Feed e Ações Rápidas</Text>
        </View>
    );
}
