import React, { useCallback } from 'react';
import { ScrollView, View, Text, RefreshControl, SafeAreaView } from 'react-native';
import { useNavigation, useFocusEffect } from '@react-navigation/native';
import { useHomeData } from '../hooks/useHomeData';
import { WelcomeHeader } from '../components/WelcomeHeader';
import { QuickStepsTutorial } from '../components/QuickStepsTutorial';
import { NextClassCard } from '../components/NextClassCard';
import { LessonProgressBar } from '../components/LessonProgressBar';
import { LoadingState } from '../../../../shared/components/LoadingState';

export function HomeScreen() {
    const navigation = useNavigation<any>();
    const {
        profile,
        nextLesson,
        completedLessons,
        isLoading,
        refetch
    } = useHomeData();

    useFocusEffect(
        useCallback(() => {
            refetch();
        }, [refetch])
    );

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
                <QuickStepsTutorial
                    onStepPress={(id) => {
                        if (id === '1') {
                            navigation.navigate('Profile', { screen: 'PersonalInfo' });
                        } else if (id === '2') {
                            navigation.navigate('Search');
                        }
                    }}
                />

                {/* 2. Next Lesson Card */}
                <NextClassCard
                    booking={nextLesson}
                    onPressDetails={(booking) => {
                        navigation.navigate('Scheduling', {
                            screen: 'LessonDetails',
                            params: { schedulingId: booking.id }
                        });
                    }}
                    onSeeAll={() => {
                        navigation.navigate('Scheduling', {
                            screen: 'MyLessons'
                        });
                    }}
                    onBookFirst={() => {
                        navigation.navigate('Search');
                    }}
                />

                {/* 3. Progress Bar */}
                <LessonProgressBar
                    completedLessons={completedLessons}
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
