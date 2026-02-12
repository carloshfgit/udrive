import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, Dimensions } from 'react-native';
import { User, Calendar, MapPin, CreditCard } from 'lucide-react-native';

const { width } = Dimensions.get('window');
const CARD_WIDTH = width * 0.75;

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
        description: 'Adicione sua foto e informe seus dados para começar.',
        icon: <User size={24} color="#3B82F6" />,
        color: 'bg-blue-50',
    },
    {
        id: '2',
        title: 'Encontre um Instrutor',
        description: 'Busque instrutores próximos a você.',
        icon: <MapPin size={24} color="#10B981" />,
        color: 'bg-emerald-50',
    },
    {
        id: '3',
        title: 'Agende sua Aula',
        description: 'Escolha o melhor horário na agenda do instrutor.',
        icon: <Calendar size={24} color="#F59E0B" />,
        color: 'bg-amber-50',
    },
    {
        id: '4',
        title: 'Pagamento Seguro',
        description: 'Pague suas aulas com cartão ou Pix via app.',
        icon: <CreditCard size={24} color="#8B5CF6" />,
        color: 'bg-purple-50',
    },
];

export function QuickStepsTutorial() {
    return (
        <View className="py-6">
            <View className="px-6 mb-4">
                <Text className="text-neutral-900 text-lg font-black tracking-tight">
                    Passos Rápidos ⚡️
                </Text>
            </View>

            <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={{ paddingHorizontal: 24 }}
                snapToInterval={CARD_WIDTH + 16}
                decelerationRate="fast"
            >
                {STEPS.map((step) => (
                    <TouchableOpacity
                        key={step.id}
                        activeOpacity={0.8}
                        style={{ width: CARD_WIDTH }}
                        className={`mr-4 p-5 rounded-3xl ${step.color} border border-white shadow-sm`}
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
        </View>
    );
}
