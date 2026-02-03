/**
 * GoDrive Mobile - FilterModal Component
 *
 * Modal de filtros para busca de instrutores.
 */

import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { BottomSheet } from '../../../../shared/components';
import { SearchFilters } from '../hooks/useInstructorSearch';

interface FilterModalProps {
    visible: boolean;
    onClose: () => void;
    filters: SearchFilters;
    onApply: (filters: SearchFilters) => void;
}

const CATEGORIES = ['A', 'B', 'AB', 'C', 'D', 'E'];
const RATINGS = [4.5, 4.0, 3.5, 3.0];
const DISTANCE_OPTIONS = [
    { value: 5, label: '5 km' },
    { value: 10, label: '10 km' },
    { value: 20, label: '20 km' },
    { value: 50, label: '50 km' },
    { value: undefined, label: 'Qualquer' },
];

/**
 * Modal de filtros usando BottomSheet.
 */
export function FilterModal({ visible, onClose, filters, onApply }: FilterModalProps) {
    const [localFilters, setLocalFilters] = useState<SearchFilters>(filters);

    const handleApply = () => {
        onApply(localFilters);
        onClose();
    };

    const handleReset = () => {
        setLocalFilters({});
    };

    const toggleCategory = (category: string) => {
        setLocalFilters(prev => ({
            ...prev,
            category: prev.category === category ? undefined : category,
        }));
    };

    return (
        <BottomSheet isVisible={visible} onClose={onClose} title="Filtros">
            <ScrollView className="px-4 pb-8" showsVerticalScrollIndicator={false}>
                {/* Categoria */}
                <View className="mb-6">
                    <Text className="text-neutral-900 text-base font-semibold mb-3">
                        Categoria da CNH
                    </Text>
                    <View className="flex-row flex-wrap gap-2">
                        {CATEGORIES.map(cat => (
                            <TouchableOpacity
                                key={cat}
                                onPress={() => toggleCategory(cat)}
                                className={`px-4 py-2 rounded-full border ${localFilters.category === cat
                                    ? 'bg-primary-500 border-primary-500'
                                    : 'bg-white border-neutral-200'
                                    }`}
                            >
                                <Text
                                    className={`text-sm font-medium ${localFilters.category === cat
                                        ? 'text-white'
                                        : 'text-neutral-700'
                                        }`}
                                >
                                    Categoria {cat}
                                </Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                </View>

                {/* Gênero do Instrutor */}
                <View className="mb-6">
                    <Text className="text-neutral-900 text-base font-semibold mb-3">
                        Gênero do Instrutor
                    </Text>
                    <View className="flex-row gap-2">
                        {['Masculino', 'Feminino'].map(gender => (
                            <TouchableOpacity
                                key={gender}
                                onPress={() =>
                                    setLocalFilters(prev => ({
                                        ...prev,
                                        biological_sex: prev.biological_sex === gender ? undefined : gender,
                                    }))
                                }
                                className={`px-4 py-2 rounded-full border ${localFilters.biological_sex === gender
                                    ? 'bg-primary-500 border-primary-500'
                                    : 'bg-white border-neutral-200'
                                    }`}
                            >
                                <Text
                                    className={`text-sm font-medium ${localFilters.biological_sex === gender
                                        ? 'text-white'
                                        : 'text-neutral-700'
                                        }`}
                                >
                                    {gender}
                                </Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                </View>

                {/* Distância */}
                <View className="mb-6">
                    <Text className="text-neutral-900 text-base font-semibold mb-3">
                        Distância máxima
                    </Text>
                    <View className="flex-row flex-wrap gap-2">
                        {DISTANCE_OPTIONS.map(option => (
                            <TouchableOpacity
                                key={String(option.value)}
                                onPress={() =>
                                    setLocalFilters(prev => ({
                                        ...prev,
                                        radiusKm: option.value,
                                    }))
                                }
                                className={`px-4 py-2 rounded-full border ${localFilters.radiusKm === option.value
                                    ? 'bg-primary-500 border-primary-500'
                                    : 'bg-white border-neutral-200'
                                    }`}
                            >
                                <Text
                                    className={`text-sm font-medium ${localFilters.radiusKm === option.value
                                        ? 'text-white'
                                        : 'text-neutral-700'
                                        }`}
                                >
                                    {option.label}
                                </Text>
                            </TouchableOpacity>
                        ))}
                    </View>
                </View>

                {/* Botões de ação */}
                <View className="flex-row gap-3 mt-4">
                    <TouchableOpacity
                        onPress={handleReset}
                        className="flex-1 py-3 rounded-xl border border-neutral-200"
                    >
                        <Text className="text-neutral-700 text-center font-semibold">Limpar</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                        onPress={handleApply}
                        className="flex-1 py-3 rounded-xl bg-primary-500"
                    >
                        <Text className="text-white text-center font-semibold">Aplicar</Text>
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </BottomSheet>
    );
}
