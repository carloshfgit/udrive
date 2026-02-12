import React from 'react';
import { View, Text, SafeAreaView, ScrollView, RefreshControl } from 'react-native';
import { useAuthStore } from '../../../lib/store';
import { Card } from '../../../shared/components';
import { InstructorWelcomeHeader } from '../components/home/InstructorWelcomeHeader';
import { InstructorQuickSteps } from '../components/home/InstructorQuickSteps';
import { InstructorEarningsSection } from '../components/home/InstructorEarningsSection';
import { ScheduleCard } from '../components/ScheduleCard';
import { useInstructorHome } from '../hooks/useInstructorHome';
import {
    useConfirmScheduling,
    useCompleteScheduling,
    useCancelScheduling,
    useRequestReschedule
} from '../hooks/useInstructorSchedule';
import { useNavigation } from '@react-navigation/native';

export function InstructorHomeScreen() {
    const { user } = useAuthStore();
    const navigation = useNavigation<any>();

    // Hooks de dados da Home
    const {
        nextClass,
        dailySummary,
        isLoading,
        refetch,
    } = useInstructorHome();

    // Hooks de mutação (reutilizados da agenda)
    const { mutate: confirm, isPending: isConfirming } = useConfirmScheduling();
    const { mutate: complete, isPending: isCompleting } = useCompleteScheduling();
    const { mutate: cancel, isPending: isCancelling } = useCancelScheduling();

    const handleReschedule = (scheduling: any) => {
        navigation.navigate('InstructorSchedule', {
            screen: 'Reschedule',
            params: { scheduling }
        });
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            <InstructorWelcomeHeader
                name={user?.full_name}
                avatarUrl={user?.avatarUrl}
            />

            <ScrollView
                className="flex-1"
                contentContainerStyle={{ paddingBottom: 32 }}
                showsVerticalScrollIndicator={false}
                refreshControl={
                    <RefreshControl refreshing={isLoading} onRefresh={refetch} />
                }
            >
                {/* Tutorial / Quick Steps */}
                <InstructorQuickSteps />

                {/* Próxima Aula */}
                <View className="px-6 mb-6">
                    <Text className="text-neutral-900 text-lg font-black tracking-tight mb-4">
                        Próxima Aula 📅
                    </Text>
                    {nextClass ? (
                        <ScheduleCard
                            scheduling={nextClass}
                            onConfirm={(id) => confirm(id)}
                            onComplete={(id) => complete(id)}
                            onCancel={(id) => cancel({ schedulingId: id })}
                            onReschedule={handleReschedule}
                            isConfirming={isConfirming}
                            isCompleting={isCompleting}
                            isCancelling={isCancelling}
                        />
                    ) : (
                        <Card variant="outlined" className="p-8 border-neutral-100 bg-neutral-50 rounded-[32px] items-center justify-center">
                            <Text className="text-neutral-400 text-center font-medium">
                                Nenhuma aula confirmada para os próximos dias.
                            </Text>
                        </Card>
                    )}
                </View>

                {/* Ganhos do Dia */}
                <InstructorEarningsSection
                    total={dailySummary?.total || 0}
                    count={dailySummary?.count || 0}
                    isLoading={isLoading}
                />

                {/* Seção de Avisos (Placeholder conforme solicitado) */}
                <View className="px-6 mb-8">
                    <Text className="text-neutral-900 text-lg font-black tracking-tight mb-4">
                        Avisos 📢
                    </Text>
                    <Card variant="outlined" className="p-6 border-neutral-100 bg-white rounded-[32px] border-dashed">
                        <Text className="text-neutral-400 text-center italic">
                            Seção de avisos em breve...
                        </Text>
                    </Card>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
