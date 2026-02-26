/**
 * InstructorPricingScreen
 *
 * Tela para o instrutor definir os valores das aulas por categoria (A/B)
 * e por tipo de veículo (instrutor/aluno).
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
    TextInput,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { ChevronLeft, DollarSign, Car, Lightbulb } from 'lucide-react-native';

import { useInstructorProfile, useUpdateInstructorProfile } from '../hooks/useInstructorProfile';

// Categorias disponíveis para seleção
const LICENSE_OPTIONS = ['A', 'B', 'AB'] as const;
type LicenseOption = (typeof LICENSE_OPTIONS)[number];

// Formatar valor monetário para exibição
function formatCurrencyInput(text: string): string {
    return text.replace(/[^\d.,]/g, '').replace(',', '.');
}

// Componente de input de preço individual
interface PriceInputProps {
    label: string;
    value: string;
    onChangeText: (text: string) => void;
    disabled?: boolean;
}

function PriceInput({ label, value, onChangeText, disabled = false }: PriceInputProps) {
    return (
        <View className="mb-4">
            <Text className={`text-sm font-semibold mb-1.5 ${disabled ? 'text-gray-400' : 'text-gray-900'}`}>
                {label}
            </Text>
            <View
                className={`
                    flex-row items-center rounded-xl overflow-hidden border-2
                    ${disabled
                        ? 'bg-gray-100 border-gray-200 opacity-60'
                        : 'bg-white border-blue-600'
                    }
                `}
            >
                <View className={`pl-4 py-3 justify-center items-center ${disabled ? '' : 'bg-blue-50 px-4'}`}>
                    <Text className={`text-base font-bold ${disabled ? 'text-gray-400' : 'text-blue-600'}`}>
                        R$
                    </Text>
                </View>
                <TextInput
                    value={value}
                    onChangeText={(t) => onChangeText(formatCurrencyInput(t))}
                    placeholder="0.00"
                    keyboardType="decimal-pad"
                    editable={!disabled}
                    className={`flex-1 text-lg px-4 py-3.5 ${disabled ? 'text-gray-400' : 'text-gray-900 font-bold'}`}
                    placeholderTextColor="#9CA3AF"
                />
            </View>
            {disabled && (
                <Text className="text-xs text-gray-400 mt-1 ml-1">
                    Indisponível para a categoria selecionada
                </Text>
            )}
        </View>
    );
}

// Componente de seleção da categoria
interface CategorySelectorProps {
    selected: LicenseOption;
    onSelect: (category: LicenseOption) => void;
}

function CategorySelector({ selected, onSelect }: CategorySelectorProps) {
    return (
        <View className="mb-6">
            <Text className="text-base font-semibold text-gray-900 mb-2">
                Categoria
            </Text>
            <Text className="text-xs text-gray-500 mb-3">
                Selecione a(s) categoria(s) que você ministra aulas
            </Text>
            <View className="flex-row gap-3">
                {LICENSE_OPTIONS.map((option) => {
                    const isSelected = selected === option;
                    return (
                        <TouchableOpacity
                            key={option}
                            onPress={() => onSelect(option)}
                            className={`
                                flex-1 py-3.5 rounded-xl border-2 items-center justify-center
                                ${isSelected
                                    ? 'bg-blue-600 border-blue-600'
                                    : 'bg-white border-gray-200'
                                }
                            `}
                        >
                            <Text
                                className={`
                                    text-lg font-bold
                                    ${isSelected ? 'text-white' : 'text-gray-700'}
                                `}
                            >
                                {option}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </View>
        </View>
    );
}

// Seção de preços por tipo de veículo
interface PriceSectionProps {
    title: string;
    description: string;
    icon: React.ReactNode;
    priceA: string;
    onChangePriceA: (text: string) => void;
    priceB: string;
    onChangePriceB: (text: string) => void;
    disabledA: boolean;
    disabledB: boolean;
}

function PriceSection({
    title,
    description,
    icon,
    priceA,
    onChangePriceA,
    priceB,
    onChangePriceB,
    disabledA,
    disabledB,
}: PriceSectionProps) {
    return (
        <View className="mb-6 bg-gray-50 border border-gray-100 rounded-2xl p-4">
            {/* Header da seção */}
            <View className="flex-row items-center mb-1">
                {icon}
                <Text className="text-base font-semibold text-gray-900 ml-2">
                    {title}
                </Text>
            </View>
            <Text className="text-xs text-gray-500 mb-4">{description}</Text>

            {/* Inputs de preço */}
            <PriceInput
                label="Categoria A (Moto)"
                value={priceA}
                onChangeText={onChangePriceA}
                disabled={disabledA}
            />
            <PriceInput
                label="Categoria B (Carro)"
                value={priceB}
                onChangeText={onChangePriceB}
                disabled={disabledB}
            />
        </View>
    );
}

export function InstructorPricingScreen() {
    const navigation = useNavigation();
    const { data: profile, isLoading } = useInstructorProfile();
    const updateProfile = useUpdateInstructorProfile();

    // Estado local
    const [licenseCategory, setLicenseCategory] = useState<LicenseOption>('B');
    const [priceAInstructor, setPriceAInstructor] = useState('');
    const [priceBInstructor, setPriceBInstructor] = useState('');
    const [priceAStudent, setPriceAStudent] = useState('');
    const [priceBStudent, setPriceBStudent] = useState('');

    // Carregar dados do perfil
    useEffect(() => {
        if (profile) {
            const cat = profile.license_category as LicenseOption;
            if (LICENSE_OPTIONS.includes(cat)) {
                setLicenseCategory(cat);
            }
            setPriceAInstructor(profile.price_cat_a_instructor_vehicle?.toString() || '');
            setPriceBInstructor(profile.price_cat_b_instructor_vehicle?.toString() || '');
            setPriceAStudent(profile.price_cat_a_student_vehicle?.toString() || '');
            setPriceBStudent(profile.price_cat_b_student_vehicle?.toString() || '');
        }
    }, [profile]);

    // Determinar quais inputs ficam bloqueados
    const isADisabled = licenseCategory === 'B';
    const isBDisabled = licenseCategory === 'A';

    // Salvar preços
    const handleSave = useCallback(async () => {
        try {
            // Validar que ao menos um preço foi preenchido para as categorias ativas
            const hasAnyPrice = [
                !isADisabled && priceAInstructor,
                !isADisabled && priceAStudent,
                !isBDisabled && priceBInstructor,
                !isBDisabled && priceBStudent,
            ].some(Boolean);

            if (!hasAnyPrice) {
                Alert.alert('Atenção', 'Preencha pelo menos um valor de aula.');
                return;
            }

            // Validar valores numéricos
            const parsePrice = (val: string): number | undefined => {
                if (!val) return undefined;
                const num = parseFloat(val);
                if (isNaN(num) || num < 0) return undefined;
                return num;
            };

            const priceCatAInstructor = isADisabled ? undefined : parsePrice(priceAInstructor);
            const priceCatBInstructor = isBDisabled ? undefined : parsePrice(priceBInstructor);
            const priceCatAStudent = isADisabled ? undefined : parsePrice(priceAStudent);
            const priceCatBStudent = isBDisabled ? undefined : parsePrice(priceBStudent);

            await updateProfile.mutateAsync({
                license_category: licenseCategory,
                price_cat_a_instructor_vehicle: priceCatAInstructor,
                price_cat_a_student_vehicle: priceCatAStudent,
                price_cat_b_instructor_vehicle: priceCatBInstructor,
                price_cat_b_student_vehicle: priceCatBStudent,
            });

            Alert.alert('Sucesso', 'Seus preços foram atualizados!');
            navigation.goBack();
        } catch (error) {
            console.error('[InstructorPricingScreen] Save error:', error);
            Alert.alert('Erro', 'Não foi possível salvar os preços. Tente novamente.');
        }
    }, [
        licenseCategory,
        priceAInstructor,
        priceBInstructor,
        priceAStudent,
        priceBStudent,
        isADisabled,
        isBDisabled,
        updateProfile,
        navigation,
    ]);

    if (isLoading) {
        return (
            <SafeAreaView className="flex-1 bg-white items-center justify-center">
                <ActivityIndicator size="large" color="#2563EB" />
            </SafeAreaView>
        );
    }

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
                    Meus Preços
                </Text>
                <View className="w-10" />
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerClassName="py-6"
                showsVerticalScrollIndicator={false}
                keyboardShouldPersistTaps="handled"
            >
                {/* Dica */}
                <View className="flex-row items-start bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
                    <Lightbulb size={20} color="#D97706" />
                    <View className="flex-1 ml-3">
                        <Text className="text-sm font-semibold text-amber-800">
                            Defina seus preços
                        </Text>
                        <Text className="text-xs text-amber-700 mt-1 leading-5">
                            Configure o valor das aulas por categoria e tipo de veículo.
                            Os valores definidos aqui serão exibidos para os alunos na busca.
                        </Text>
                    </View>
                </View>

                {/* Seleção de Categoria */}
                <CategorySelector
                    selected={licenseCategory}
                    onSelect={setLicenseCategory}
                />

                {/* Seção: Valor no seu veículo */}
                <PriceSection
                    title="Valor no seu veículo"
                    description="Valor da aula quando o aluno utiliza o seu veículo"
                    icon={<Car size={20} color="#2563EB" />}
                    priceA={priceAInstructor}
                    onChangePriceA={setPriceAInstructor}
                    priceB={priceBInstructor}
                    onChangePriceB={setPriceBInstructor}
                    disabledA={isADisabled}
                    disabledB={isBDisabled}
                />

                {/* Seção: Valor no veículo do aluno */}
                <PriceSection
                    title="Valor no veículo do aluno"
                    description="Valor da aula quando o aluno utiliza o próprio veículo"
                    icon={<Car size={20} color="#10B981" />}
                    priceA={priceAStudent}
                    onChangePriceA={setPriceAStudent}
                    priceB={priceBStudent}
                    onChangePriceB={setPriceBStudent}
                    disabledA={isADisabled}
                    disabledB={isBDisabled}
                />
            </ScrollView>

            {/* Botão Salvar */}
            <View className="px-4 pb-8 pt-4 border-t border-gray-100">
                <TouchableOpacity
                    onPress={handleSave}
                    disabled={updateProfile.isPending}
                    className={`
                        py-4 rounded-xl items-center justify-center
                        ${updateProfile.isPending ? 'bg-blue-400' : 'bg-blue-600 active:bg-blue-700'}
                    `}
                >
                    {updateProfile.isPending ? (
                        <ActivityIndicator size="small" color="#ffffff" />
                    ) : (
                        <Text className="text-base font-semibold text-white">
                            Salvar Preços
                        </Text>
                    )}
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
