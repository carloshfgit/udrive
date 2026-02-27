/**
 * GoDrive Mobile - LessonOptionsScreen
 *
 * Tela de seleção de categoria da CNH (A/B) e tipo de veículo
 * (instrutor/aluno) antes do agendamento de data e horário.
 */

import React, { useState, useMemo, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import {
    ChevronLeft,
    Bike,
    Car,
    User,
    CarFront,
    CheckCircle,
    ArrowRight,
} from 'lucide-react-native';

import { Avatar } from '../../../../shared/components';
import { formatPrice } from '../../../../shared';
import { SchedulingStackParamList } from './SelectDateTimeScreen';

// === Tipos ===

type LessonOptionsRouteProp = RouteProp<SchedulingStackParamList, 'LessonOptions'>;
type LessonOptionsNavigationProp = NativeStackNavigationProp<SchedulingStackParamList, 'LessonOptions'>;

type CategoryOption = 'A' | 'B';
type VehicleOption = 'instructor' | 'student';

// === Component ===

export function LessonOptionsScreen() {
    const navigation = useNavigation<LessonOptionsNavigationProp>();
    const route = useRoute<LessonOptionsRouteProp>();
    const {
        instructorId,
        instructorName,
        instructorAvatar,
        licenseCategory,
        rating,
        priceAInstructor,
        priceAStudent,
        priceBInstructor,
        priceBStudent,
    } = route.params;

    // Determinar categorias disponíveis (com pelo menos um preço)
    const availableCategories = useMemo(() => {
        const cats: CategoryOption[] = [];
        const hasA = licenseCategory.includes('A') &&
            (priceAInstructor != null || priceAStudent != null);
        const hasB = licenseCategory.includes('B') &&
            (priceBInstructor != null || priceBStudent != null);
        if (hasA) cats.push('A');
        if (hasB) cats.push('B');
        return cats;
    }, [licenseCategory, priceAInstructor, priceAStudent, priceBInstructor, priceBStudent]);

    // Estado de seleção
    const [selectedCategory, setSelectedCategory] = useState<CategoryOption | null>(null);
    const [selectedVehicle, setSelectedVehicle] = useState<VehicleOption | null>(null);

    // Auto-selecionar se só tem uma categoria
    useEffect(() => {
        if (availableCategories.length === 1) {
            setSelectedCategory(availableCategories[0]);
        }
    }, [availableCategories]);

    // Resetar veículo ao mudar categoria
    useEffect(() => {
        setSelectedVehicle(null);
    }, [selectedCategory]);

    // Opções de veículo disponíveis para a categoria selecionada
    const availableVehicles = useMemo(() => {
        if (!selectedCategory) return [];
        const vehicles: VehicleOption[] = [];
        if (selectedCategory === 'A') {
            if (priceAInstructor != null) vehicles.push('instructor');
            if (priceAStudent != null) vehicles.push('student');
        } else {
            if (priceBInstructor != null) vehicles.push('instructor');
            if (priceBStudent != null) vehicles.push('student');
        }
        return vehicles;
    }, [selectedCategory, priceAInstructor, priceAStudent, priceBInstructor, priceBStudent]);

    // Auto-selecionar se só tem um veículo
    useEffect(() => {
        if (availableVehicles.length === 1) {
            setSelectedVehicle(availableVehicles[0]);
        }
    }, [availableVehicles]);

    // Preço selecionado
    const selectedPrice = useMemo(() => {
        if (!selectedCategory || !selectedVehicle) return null;
        const map: Record<string, number | null | undefined> = {
            'A-instructor': priceAInstructor,
            'A-student': priceAStudent,
            'B-instructor': priceBInstructor,
            'B-student': priceBStudent,
        };
        return map[`${selectedCategory}-${selectedVehicle}`] ?? null;
    }, [selectedCategory, selectedVehicle, priceAInstructor, priceAStudent, priceBInstructor, priceBStudent]);

    const canContinue = selectedCategory !== null && selectedVehicle !== null && selectedPrice !== null;

    // Navegar para SelectDateTime
    const handleContinue = () => {
        if (!canContinue || selectedPrice === null) return;

        navigation.navigate('SelectDateTime', {
            instructorId,
            instructorName,
            instructorAvatar,
            selectedPrice,
            licenseCategory,
            rating,
            lessonCategory: selectedCategory!,
            vehicleOwnership: selectedVehicle!,
        });
    };

    // Labels
    const categoryLabels: Record<CategoryOption, { label: string; desc: string }> = {
        A: { label: 'Categoria A', desc: 'Moto' },
        B: { label: 'Categoria B', desc: 'Carro' },
    };

    const vehicleLabels: Record<VehicleOption, { label: string; desc: string }> = {
        instructor: { label: 'Veículo do Instrutor', desc: 'O instrutor fornece o veículo' },
        student: { label: 'Meu Veículo', desc: 'Você usa o seu próprio veículo' },
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
                <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    className="w-10 h-10 items-center justify-center"
                    accessibilityLabel="Voltar"
                >
                    <ChevronLeft size={24} color="#111318" />
                </TouchableOpacity>
                <Text className="flex-1 text-lg font-bold text-gray-900 text-center">
                    Configurar Aula
                </Text>
                <View className="w-10" />
            </View>

            <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
                {/* Info do Instrutor */}
                <View className="px-6 py-4 flex-row items-center bg-neutral-50 border-b border-neutral-100">
                    <Avatar
                        source={instructorAvatar ? { uri: instructorAvatar } : undefined}
                        fallback={instructorName.charAt(0)}
                        size="md"
                    />
                    <View className="flex-1 ml-3">
                        <Text className="text-base font-semibold text-gray-900">
                            {instructorName}
                        </Text>
                        {!!licenseCategory && (
                            <Text className="text-sm text-gray-500 mt-0.5">
                                Categoria {licenseCategory}
                            </Text>
                        )}
                    </View>

                    {/* Valor da Aula - Exibido no topo para fácil visualização */}
                    {selectedPrice !== null && (
                        <View className="items-end bg-success-50 px-3 py-1.5 rounded-lg border border-success-100">
                            <Text className="text-[10px] text-success-600 font-bold uppercase tracking-wider">
                                Valor
                            </Text>
                            <Text className="text-lg font-black text-success-700">
                                {formatPrice(selectedPrice)}
                            </Text>
                        </View>
                    )}
                </View>

                {/* Seção: Categoria */}
                <View className="px-6 pt-6">
                    <Text className="text-base font-semibold text-gray-900 mb-1">
                        Categoria da CNH
                    </Text>
                    <Text className="text-sm text-gray-500 mb-4">
                        Selecione o tipo de habilitação para a aula
                    </Text>

                    <View className="gap-3">
                        {availableCategories.map((cat) => {
                            const isSelected = selectedCategory === cat;
                            const Icon = cat === 'A' ? Bike : Car;
                            return (
                                <TouchableOpacity
                                    key={cat}
                                    onPress={() => setSelectedCategory(cat)}
                                    className={`flex-row items-center p-4 rounded-xl border-2 ${isSelected
                                        ? 'border-primary-500 bg-primary-50'
                                        : 'border-neutral-200 bg-white'
                                        }`}
                                    accessibilityLabel={`Selecionar ${categoryLabels[cat].label}`}
                                >
                                    <View
                                        className={`w-12 h-12 rounded-full items-center justify-center ${isSelected ? 'bg-primary-100' : 'bg-neutral-100'
                                            }`}
                                    >
                                        <Icon
                                            size={24}
                                            color={isSelected ? '#2563EB' : '#6B7280'}
                                        />
                                    </View>
                                    <View className="flex-1 ml-3">
                                        <Text
                                            className={`text-base font-semibold ${isSelected ? 'text-primary-700' : 'text-gray-900'
                                                }`}
                                        >
                                            {categoryLabels[cat].label}
                                        </Text>
                                        <Text className="text-sm text-gray-500">
                                            {categoryLabels[cat].desc}
                                        </Text>
                                    </View>
                                    {isSelected && (
                                        <CheckCircle size={24} color="#2563EB" />
                                    )}
                                </TouchableOpacity>
                            );
                        })}
                    </View>
                </View>

                {/* Seção: Veículo */}
                {selectedCategory && (
                    <View className="px-6 pt-6">
                        <Text className="text-base font-semibold text-gray-900 mb-1">
                            Veículo
                        </Text>
                        <Text className="text-sm text-gray-500 mb-4">
                            Escolha de quem será o veículo utilizado na aula
                        </Text>

                        <View className="gap-3">
                            {availableVehicles.map((vehicle) => {
                                const isSelected = selectedVehicle === vehicle;
                                const Icon = vehicle === 'instructor' ? CarFront : User;
                                return (
                                    <TouchableOpacity
                                        key={vehicle}
                                        onPress={() => setSelectedVehicle(vehicle)}
                                        className={`flex-row items-center p-4 rounded-xl border-2 ${isSelected
                                            ? 'border-primary-500 bg-primary-50'
                                            : 'border-neutral-200 bg-white'
                                            }`}
                                        accessibilityLabel={`Selecionar ${vehicleLabels[vehicle].label}`}
                                    >
                                        <View
                                            className={`w-12 h-12 rounded-full items-center justify-center ${isSelected ? 'bg-primary-100' : 'bg-neutral-100'
                                                }`}
                                        >
                                            <Icon
                                                size={24}
                                                color={isSelected ? '#2563EB' : '#6B7280'}
                                            />
                                        </View>
                                        <View className="flex-1 ml-3">
                                            <Text
                                                className={`text-base font-semibold ${isSelected ? 'text-primary-700' : 'text-gray-900'
                                                    }`}
                                            >
                                                {vehicleLabels[vehicle].label}
                                            </Text>
                                            <Text className="text-sm text-gray-500">
                                                {vehicleLabels[vehicle].desc}
                                            </Text>
                                        </View>
                                        {isSelected && (
                                            <CheckCircle size={24} color="#2563EB" />
                                        )}
                                    </TouchableOpacity>
                                );
                            })}
                        </View>
                    </View>
                )}



                {/* Espaço para o botão fixo */}
                <View className="h-24" />
            </ScrollView>

            {/* Botão Fixo - Avançar */}
            <View className="absolute bottom-0 left-0 right-0 px-6 pb-8 pt-4 bg-white border-t border-gray-100">
                <TouchableOpacity
                    onPress={handleContinue}
                    disabled={!canContinue}
                    className={`flex-row items-center justify-center py-4 rounded-xl ${canContinue
                        ? 'bg-primary-600 active:bg-primary-700'
                        : 'bg-neutral-200'
                        }`}
                    accessibilityLabel="Avançar para seleção de data e horário"
                >
                    <Text
                        className={`text-base font-semibold ${canContinue ? 'text-white' : 'text-neutral-400'
                            }`}
                    >
                        Escolher Data e Horário
                    </Text>
                    {canContinue && (
                        <ArrowRight size={18} color="#ffffff" className="ml-2" />
                    )}
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
