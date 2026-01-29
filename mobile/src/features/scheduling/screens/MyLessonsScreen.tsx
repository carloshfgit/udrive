import React from 'react';
import { View, Text } from 'react-native';

export function MyLessonsScreen() {
    return (
        <View className="flex-1 items-center justify-center bg-white">
            <Text className="text-2xl font-bold text-blue-600">Minhas Aulas</Text>
            <Text className="text-gray-500 mt-2">Em breve: Agendamentos e Histórico</Text>
        </View>
    );
}
