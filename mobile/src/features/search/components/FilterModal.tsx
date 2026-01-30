/**
 * GoDrive Mobile - FilterModal Component
 *
 * Modal de filtros para busca de instrutores.
 */

import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { BottomSheet } from '../../../shared/components';
import { SearchFilters } from '../hooks/useInstructorSearch';

interface FilterModalProps {
    visible: boolean;
    onClose: () => void;
    filters: SearchFilters;
    onApply: (filters: SearchFilters) => void;
}

const CATEGORIES = ['A', 'B', 'AB', 'C', 'D', 'E'];
const RATINGS = [4.5, 4.0, 3.5, 3.0];
const DISTANCE_OPTIONS = [5, 10, 20, 50];

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

                {/* Avaliação mínima */}
                <View className="mb-6">
                    <Text className="text-neutral-900 text-base font-semibold mb-3">
                        Avaliação mínima
                    </Text>
                    <View className="flex-row flex-wrap gap-2">
                        {RATINGS.map(rating => (
                            <TouchableOpacity
                                key={rating}
                                onPress={() =>
                                    setLocalFilters(prev => ({
                                        ...prev,
                                        minRating: prev.minRating === rating ? undefined : rating,
                                    }))
                                }
                                className={`px-4 py-2 rounded-full border flex-row items-center ${localFilters.minRating === rating
                                    ? 'bg-primary-500 border-primary-500'
                                    : 'bg-white border-neutral-200'
                                    }`}
                            >
                                <Text className="text-yellow-500 mr-1">★</Text>
                                <Text
                                    className={`text-sm font-medium ${localFilters.minRating === rating
                                        ? 'text-white'
                                        : 'text-neutral-700'
                                        }`}
                                >
                                    {rating}+
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
                        {DISTANCE_OPTIONS.map(distance => (
                            <TouchableOpacity
                                key={distance}
                                onPress={() =>
                                    setLocalFilters(prev => ({
                                        ...prev,
                                        radiusKm: prev.radiusKm === distance ? undefined : distance,
                                    }))
                                }
                                className={`px-4 py-2 rounded-full border ${localFilters.radiusKm === distance
                                    ? 'bg-primary-500 border-primary-500'
                                    : 'bg-white border-neutral-200'
                                    }`}
                            >
                                <Text
                                    className={`text-sm font-medium ${localFilters.radiusKm === distance
                                        ? 'text-white'
                                        : 'text-neutral-700'
                                        }`}
                                >
                                    {distance} km
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
