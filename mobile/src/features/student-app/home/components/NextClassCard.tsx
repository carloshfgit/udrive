import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { StudentLessonCard } from '../../../shared-features/scheduling/components/StudentLessonCard';
import { BookingResponse } from '../../../shared-features/scheduling/api/schedulingApi';

interface NextClassCardProps {
    booking?: BookingResponse | null;
    onPressDetails: (booking: BookingResponse) => void;
    onBookFirst?: () => void;
}

export function NextClassCard({
    booking,
    onPressDetails,
    onBookFirst
}: NextClassCardProps) {
    return (
        <View className="px-6 py-4">
            <View className="flex-row justify-between items-center mb-4">
                <Text className="text-neutral-900 text-lg font-black tracking-tight">
                    Sua Próxima Aula 🚗
                </Text>
                {booking && (
                    <TouchableOpacity activeOpacity={0.7}>
                        <Text className="text-primary-600 text-sm font-bold">Ver todas</Text>
                    </TouchableOpacity>
                )}
            </View>

            {booking ? (
                <StudentLessonCard
                    scheduling={booking}
                    onPressDetails={onPressDetails}
                    variant="student"
                />
            ) : (
                <View className="bg-neutral-50 rounded-3xl p-8 items-center border border-neutral-100 border-dashed">
                    <Text className="text-neutral-400 text-center mb-6 leading-relaxed">
                        Você ainda não tem nenhuma aula{"\n"}agendada para os próximos dias.
                    </Text>
                    <TouchableOpacity
                        onPress={onBookFirst}
                        className="bg-primary-600 px-8 py-3.5 rounded-2xl shadow-sm shadow-primary-200"
                        activeOpacity={0.8}
                    >
                        <Text className="text-white font-black">Buscar Instrutor</Text>
                    </TouchableOpacity>
                </View>
            )}
        </View>
    );
}
