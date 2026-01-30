/**
 * InstructorDashboardScreen
 *
 * Tela de dashboard/métricas do instrutor - Placeholder.
 */

import React from 'react';
import { View, Text, SafeAreaView, ScrollView } from 'react-native';
import { TrendingUp, Star, BookOpen, DollarSign } from 'lucide-react-native';
import { Card } from '../../../shared/components';

interface MetricCardProps {
    icon: React.ReactNode;
    label: string;
    value: string;
    subtext?: string;
    color: string;
}

function MetricCard({ icon, label, value, subtext, color }: MetricCardProps) {
    return (
        <Card variant="outlined" className="flex-1 min-w-[45%] mb-3">
            <View className="p-4">
                <View
                    className="w-10 h-10 rounded-lg items-center justify-center mb-3"
                    style={{ backgroundColor: `${color}15` }}
                >
                    {icon}
                </View>
                <Text className="text-gray-500 text-sm">{label}</Text>
                <Text className="text-xl font-bold text-gray-900 mt-1">{value}</Text>
                {subtext && (
                    <Text className="text-gray-400 text-xs mt-1">{subtext}</Text>
                )}
            </View>
        </Card>
    );
}

export function InstructorDashboardScreen() {
    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="px-4 py-4">
                <Text className="text-xl font-bold text-gray-900">
                    Dashboard
                </Text>
                <Text className="text-gray-500 mt-1">
                    Suas métricas e desempenho
                </Text>
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerClassName="pb-8"
                showsVerticalScrollIndicator={false}
            >
                {/* Metrics Grid */}
                <View className="flex-row flex-wrap justify-between">
                    <MetricCard
                        icon={<DollarSign size={20} color="#22c55e" />}
                        label="Ganhos do Mês"
                        value="R$ 0,00"
                        subtext="0 aulas"
                        color="#22c55e"
                    />
                    <MetricCard
                        icon={<TrendingUp size={20} color="#3b82f6" />}
                        label="Ganhos da Semana"
                        value="R$ 0,00"
                        subtext="0 aulas"
                        color="#3b82f6"
                    />
                    <MetricCard
                        icon={<BookOpen size={20} color="#8b5cf6" />}
                        label="Aulas Realizadas"
                        value="0"
                        subtext="Este mês"
                        color="#8b5cf6"
                    />
                    <MetricCard
                        icon={<Star size={20} color="#f59e0b" />}
                        label="Avaliação Média"
                        value="—"
                        subtext="0 avaliações"
                        color="#f59e0b"
                    />
                </View>

                {/* Gráfico Placeholder */}
                <Card variant="outlined" className="mt-4">
                    <View className="p-4">
                        <Text className="text-lg font-semibold text-gray-900 mb-4">
                            📊 Evolução de Ganhos
                        </Text>
                        <View className="h-40 bg-gray-50 rounded-lg items-center justify-center">
                            <TrendingUp size={48} color="#d1d5db" />
                            <Text className="text-gray-400 mt-2">
                                Gráfico em desenvolvimento
                            </Text>
                        </View>
                    </View>
                </Card>

                {/* Info */}
                <View className="bg-gray-50 p-4 rounded-xl mt-4">
                    <Text className="text-gray-600 text-sm text-center">
                        Suas métricas serão atualizadas conforme você realizar aulas.
                    </Text>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
