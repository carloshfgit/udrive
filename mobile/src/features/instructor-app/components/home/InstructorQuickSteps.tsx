import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, useWindowDimensions, NativeSyntheticEvent, NativeScrollEvent } from 'react-native';
import Animated, { useAnimatedStyle, withTiming } from 'react-native-reanimated';
import { User, Calendar, CheckSquare, CreditCard, MessageSquare } from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';

const GAP = 12;

interface TutorialStep {
    id: string;
    title: string;
    description: string;
    icon: React.ReactNode;
    color: string;
    onPress?: () => void;
}

const STEPS: TutorialStep[] = [
    {
        id: '1',
        title: 'Complete seu Perfil',
        description: 'Toque aqui para adicionar sua foto e informações para atrair alunos.',
        icon: <User size={24} color="#3B82F6" />,
        color: 'bg-blue-50',
    },
    {
        id: '2',
        title: 'Receba sem Taxas!',
        description: 'Crie e conecte sua conta Stripe para receber seus pagamentos de forma integral.',
        icon: <CreditCard size={24} color="#8B5CF6" />,
        color: 'bg-purple-50',
    },
    {
        id: '3',
        title: 'Configure sua Agenda',
        description: 'Defina os horários em que você está disponível.',
        icon: <Calendar size={24} color="#10B981" />,
        color: 'bg-emerald-50',
    },
    {
        id: '4',
        title: 'Aceite Aulas',
        description: 'Fique atento às notificações de novos agendamentos.',
        icon: <CheckSquare size={24} color="#F59E0B" />,
        color: 'bg-amber-50',
    },
    {
        id: '5',
        title: 'Converse com seu Aluno',
        description: 'Defina o ponto de encontro e tire as dúvidas.',
        icon: <MessageSquare size={24} color="#5cb3f6ff" />,
        color: 'bg-blue-50',
    },
];

export function InstructorQuickSteps() {
    const { width } = useWindowDimensions();
    const CARD_WIDTH = Math.min(width * 0.8, 340);
    const navigation = useNavigation<any>();
    const [activeIndex, setActiveIndex] = useState(0);
    const scrollViewRef = React.useRef<ScrollView>(null);

    const handleStepPress = (id: string) => {
        switch (id) {
            case '1': // Complete seu Perfil
                navigation.navigate('InstructorProfile', { screen: 'EditPublicProfile' });
                break;
            case '3': // Configure sua Agenda
                navigation.navigate('InstructorSchedule', { screen: 'InstructorAvailability' });
                break;
            case '4': // Aceite Aulas
                navigation.navigate('InstructorSchedule', { screen: 'InstructorScheduleMain' });
                break;
            case '5': // Converse com seu Aluno
                navigation.navigate('InstructorChat');
                break;
            default:
                break;
        }
    };

    React.useEffect(() => {
        const interval = setInterval(() => {
            const nextIndex = (activeIndex + 1) % STEPS.length;
            scrollViewRef.current?.scrollTo({
                x: nextIndex * (CARD_WIDTH + GAP),
                animated: true,
            });
            setActiveIndex(nextIndex);
        }, 5000);

        return () => clearInterval(interval);
    }, [activeIndex, CARD_WIDTH]);

    const handleScroll = (event: NativeSyntheticEvent<NativeScrollEvent>) => {
        const scrollOffset = event.nativeEvent.contentOffset.x;
        const index = Math.round(scrollOffset / (CARD_WIDTH + GAP));
        if (index !== activeIndex) {
            setActiveIndex(index);
        }
    };

    return (
        <View className="py-6">
            <View className="px-6 mb-4">
                <Text className="text-neutral-900 text-lg font-black tracking-tight">
                    Siga esses passos para começar ⚡️
                </Text>
            </View>

            <ScrollView
                ref={scrollViewRef}
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={{ paddingHorizontal: 24 }}
                snapToInterval={CARD_WIDTH + GAP}
                snapToAlignment="start"
                decelerationRate="fast"
                onScroll={handleScroll}
                scrollEventThrottle={16}
            >
                {STEPS.map((step) => (
                    <TouchableOpacity
                        key={step.id}
                        activeOpacity={0.8}
                        onPress={() => handleStepPress(step.id)}
                        style={{ width: CARD_WIDTH }}
                        className={`mr-3 p-5 rounded-3xl ${step.color} border border-white shadow-sm`}
                    >
                        <View className="w-12 h-12 bg-white rounded-2xl items-center justify-center mb-4 shadow-sm">
                            {step.icon}
                        </View>
                        <Text className="text-neutral-900 font-bold text-lg mb-1 leading-tight">
                            {step.title}
                        </Text>
                        <Text className="text-neutral-500 text-sm leading-snug">
                            {step.description}
                        </Text>
                    </TouchableOpacity>
                ))}
            </ScrollView>

            {/* Pagination Indicators */}
            <View className="flex-row justify-center mt-6 gap-2">
                {STEPS.map((_, index) => {
                    const isActive = index === activeIndex;
                    const animatedStyle = useAnimatedStyle(() => ({
                        width: withTiming(isActive ? 24 : 6, { duration: 300 }),
                        backgroundColor: withTiming(
                            isActive ? '#2563EB' : '#E5E7EB', // primary-600 vs neutral-200
                            { duration: 300 }
                        ),
                    }));

                    return (
                        <Animated.View
                            key={index}
                            style={[{ height: 6, borderRadius: 999 }, animatedStyle]}
                        />
                    );
                })}
            </View>
        </View>
    );
}
