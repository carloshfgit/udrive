import React from 'react';
import { View, Text } from 'react-native';
import { TrendingUp, Wallet } from 'lucide-react-native';
import { Card } from '../../../../shared/components';

interface InstructorEarningsSectionProps {
    total: number;
    count: number;
    isLoading?: boolean;
}

export function InstructorEarningsSection({
    total = 0,
    count = 0,
    isLoading = false,
}: InstructorEarningsSectionProps) {
    return (
        <View className="px-6 mb-6">
            <View className="mb-4 flex-row items-center justify-between">
                <Text className="text-neutral-900 text-lg font-black tracking-tight">
                    Ganhos do Dia 💰
                </Text>
                <View className="flex-row items-center bg-emerald-50 px-2 py-1 rounded-lg">
                    <TrendingUp size={14} color="#10B981" />
                    <Text className="text-emerald-700 text-[10px] font-bold ml-1 uppercase">
                        Hoje
                    </Text>
                </View>
            </View>

            <Card variant="outlined" className="p-6 border-neutral-100 bg-white shadow-sm rounded-[32px]">
                <View className="flex-row items-center">
                    <View className="w-14 h-14 bg-blue-50 rounded-2xl items-center justify-center mr-4">
                        <Wallet size={28} color="#2563EB" />
                    </View>
                    <View>
                        <Text className="text-neutral-400 text-xs font-bold uppercase tracking-widest mb-1">
                            Total Recebido
                        </Text>
                        <Text className="text-neutral-900 text-3xl font-black tracking-tighter">
                            R$ {total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </Text>
                    </View>
                </View>

                <View className="h-[1px] bg-neutral-50 my-5" />

                <View className="flex-row items-center justify-between">
                    <View>
                        <Text className="text-neutral-400 text-[10px] font-bold uppercase tracking-tight">
                            Aulas Finalizadas
                        </Text>
                        <Text className="text-neutral-900 text-lg font-black">
                            {count} {count === 1 ? 'aula' : 'aulas'}
                        </Text>
                    </View>
                    <View className="bg-blue-600 px-4 py-2 rounded-xl">
                        <Text className="text-white font-bold text-xs">Ver Detalhes</Text>
                    </View>
                </View>
            </Card>
        </View>
    );
}
