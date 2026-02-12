import React from 'react';
import { ScrollView, View, Text, RefreshControl, SafeAreaView } from 'react-native';
import { useHomeData } from '../hooks/useHomeData';
import { WelcomeHeader } from '../components/WelcomeHeader';
import { QuickStepsTutorial } from '../components/QuickStepsTutorial';
import { NextClassCard } from '../components/NextClassCard';
import { LessonProgressBar } from '../components/LessonProgressBar';
import { LoadingState } from '../../../../shared/components/LoadingState';

export function HomeScreen() {
    const {
        profile,
        nextLesson,
        isLoading,
        refetch
    } = useHomeData();

    if (isLoading && !profile) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                <View className="px-6 py-8">
                    <LoadingState.Card />
                    <LoadingState.ListItem />
                    <LoadingState.ListItem />
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-white">
            <WelcomeHeader
                name={profile?.full_name}
                notificationCount={0}
            />

            <ScrollView
                className="flex-1"
                showsVerticalScrollIndicator={false}
                refreshControl={
                    <RefreshControl refreshing={isLoading} onRefresh={refetch} />
                }
            >
                {/* 1. Tutorial Carousel */}
                <QuickStepsTutorial />

                {/* 2. Next Lesson Card */}
                <NextClassCard
                    booking={nextLesson}
                    onPressDetails={(booking) => {
                        console.log('Ver detalhes:', booking.id);
                        // TODO: Navigate to lesson details
                    }}
                    onBookFirst={() => {
                        console.log('Buscar instrutor');
                        // TODO: Navigate to search/map
                    }}
                />

                {/* 3. Progress Bar */}
                <LessonProgressBar
                    completedLessons={profile?.total_lessons || 0}
                    totalGoal={10}
                />

                {/* 4. Announcements Placeholder */}
                <View className="px-6 py-4 mb-10">
                    <Text className="text-neutral-900 text-lg font-black tracking-tight mb-4">
                        Avisos e Novidades 📢
                    </Text>
                    <View className="bg-neutral-50 rounded-3xl p-6 border border-neutral-100 items-center justify-center">
                        <Text className="text-neutral-400 text-sm font-medium">
                            Nenhum aviso importante no momento.
                        </Text>
                    </View>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
