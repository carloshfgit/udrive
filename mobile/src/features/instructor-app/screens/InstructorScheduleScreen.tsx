/**
 * InstructorScheduleScreen
 *
 * Tela de agenda do instrutor - Placeholder.
 */

import React from 'react';
import { View, Text, SafeAreaView, ScrollView, TouchableOpacity } from 'react-native';
import { Calendar, Clock, Plus } from 'lucide-react-native';
import { Card } from '../../../shared/components';

export function InstructorScheduleScreen() {
    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="px-4 py-4 flex-row items-center justify-between">
                <Text className="text-xl font-bold text-gray-900">
                    Minha Agenda
                </Text>
                <TouchableOpacity
                    className="bg-blue-600 px-4 py-2 rounded-lg flex-row items-center"
                    accessibilityLabel="Definir disponibilidade"
                >
                    <Plus size={18} color="#ffffff" />
                    <Text className="text-white font-semibold ml-1">
                        Horários
                    </Text>
                </TouchableOpacity>
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerClassName="pb-8"
                showsVerticalScrollIndicator={false}
            >
                {/* Calendário Placeholder */}
                <Card variant="outlined" className="mb-4">
                    <View className="p-4 items-center">
                        <Calendar size={48} color="#2563EB" />
                        <Text className="text-gray-500 mt-3 text-center">
                            Calendário de disponibilidade{'\n'}em desenvolvimento
                        </Text>
                    </View>
                </Card>

                {/* Lista de Horários */}
                <View className="mb-4">
                    <Text className="text-lg font-semibold text-gray-900 mb-3">
                        Horários de Hoje
                    </Text>

                    <Card variant="outlined" className="mb-3">
                        <View className="p-4 flex-row items-center">
                            <View className="w-12 h-12 rounded-full bg-blue-50 items-center justify-center">
                                <Clock size={24} color="#2563EB" />
                            </View>
                            <View className="ml-4 flex-1">
                                <Text className="text-gray-400">
                                    Nenhuma aula agendada
                                </Text>
                            </View>
                        </View>
                    </Card>
                </View>

                {/* Dica */}
                <View className="bg-blue-50 p-4 rounded-xl">
                    <Text className="text-blue-800 font-medium">
                        💡 Dica
                    </Text>
                    <Text className="text-blue-700 text-sm mt-1">
                        Configure seus horários disponíveis para que alunos possam agendar aulas com você.
                    </Text>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
