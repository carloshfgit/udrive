import React from 'react';
import { View, Text } from 'react-native';
import { ProgressBar } from '../../../../shared/components/ProgressBar';

interface LessonProgressBarProps {
    completedLessons: number;
    totalGoal?: number;
}

export function LessonProgressBar({
    completedLessons,
    totalGoal = 10
}: LessonProgressBarProps) {
    const percentage = Math.min(100, (completedLessons / totalGoal) * 100);

    return (
        <View className="px-6 py-6">
            <View className="bg-neutral-900 rounded-[32px] p-6 shadow-xl shadow-neutral-400">
                <View className="flex-row justify-between items-center mb-4">
                    <View>
                        <Text className="text-neutral-400 text-[10px] uppercase font-bold tracking-[2px] mb-1">
                            PROGRESSO TOTAL
                        </Text>
                        <Text className="text-white text-2xl font-black">
                            {completedLessons} / {totalGoal} <Text className="text-neutral-500 text-lg">aulas</Text>
                        </Text>
                    </View>
                    <View className="bg-primary-600 px-3 py-1.5 rounded-xl">
                        <Text className="text-white font-bold text-xs">{Math.round(percentage)}%</Text>
                    </View>
                </View>

                <ProgressBar
                    progress={percentage}
                    height={8}
                    color="#D1D5DB"
                    className="bg-neutral-800"
                />

                <Text className="text-neutral-500 text-xs mt-4 font-medium leading-relaxed">
                    Você completou {completedLessons} das {totalGoal} aulas recomendadas para sua categoria.
                </Text>
            </View>
        </View>
    );
}
