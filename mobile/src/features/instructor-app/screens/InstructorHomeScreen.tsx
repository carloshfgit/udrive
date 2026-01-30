/**
 * InstructorHomeScreen
 *
 * Tela inicial/feed do instrutor - Placeholder.
 */

import React from 'react';
import { View, Text, SafeAreaView, ScrollView } from 'react-native';
import { useAuthStore } from '../../../lib/store';
import { Card } from '../../../shared/components';

export function InstructorHomeScreen() {
    const { user } = useAuthStore();

    const firstName = user?.full_name?.split(' ')[0] || 'Instrutor';

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="px-4 py-4">
                <Text className="text-2xl font-bold text-gray-900">
                    Olá, {firstName}! 👋
                </Text>
                <Text className="text-gray-500 mt-1">
                    Confira seu dia de trabalho
                </Text>
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerClassName="pb-8"
                showsVerticalScrollIndicator={false}
            >
                {/* Card: Próximas Aulas */}
                <Card variant="outlined" className="mb-4">
                    <View className="p-4">
                        <Text className="text-lg font-semibold text-gray-900">
                            📅 Próximas Aulas
                        </Text>
                        <Text className="text-gray-500 mt-2">
                            Você não tem aulas agendadas para hoje.
                        </Text>
                    </View>
                </Card>

                {/* Card: Ganhos do Dia */}
                <Card variant="outlined" className="mb-4">
                    <View className="p-4">
                        <Text className="text-lg font-semibold text-gray-900">
                            💰 Ganhos de Hoje
                        </Text>
                        <Text className="text-3xl font-bold text-blue-600 mt-2">
                            R$ 0,00
                        </Text>
                        <Text className="text-gray-400 text-sm mt-1">
                            0 aulas realizadas
                        </Text>
                    </View>
                </Card>

                {/* Card: Avisos */}
                <Card variant="outlined" className="mb-4">
                    <View className="p-4">
                        <Text className="text-lg font-semibold text-gray-900">
                            📢 Avisos
                        </Text>
                        <Text className="text-gray-500 mt-2">
                            Nenhum aviso no momento.
                        </Text>
                    </View>
                </Card>
            </ScrollView>
        </SafeAreaView>
    );
}
