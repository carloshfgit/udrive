/**
 * GoDrive Mobile - InstructorCard Component
 *
 * Card de instrutor conforme design de referência.
 */

import React, { memo } from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import { Instructor } from '../api/searchApi';

interface InstructorCardProps {
    instructor: Instructor;
    onViewProfile: (id: string) => void;
}

/**
 * Card de instrutor exibindo:
 * - Rating + número de avaliações
 * - Nome do instrutor
 * - Veículo + categoria
 * - Preço por hora
 * - Botão "Ver Perfil"
 * - Avatar à direita
 */
function InstructorCardComponent({ instructor, onViewProfile }: InstructorCardProps) {
    const {
        id,
        name,
        rating,
        total_reviews,
        vehicle_type,
        license_category,
        hourly_rate,
        avatar_url,
    } = instructor;

    // Fallback para nome se não vier da API
    const displayName = name || 'Instrutor';

    return (
        <View className="mx-4 my-2">
            <View className="flex-row items-stretch justify-between gap-4 rounded-xl bg-white p-4 shadow-sm border border-neutral-100">
                {/* Conteúdo à esquerda */}
                <View className="flex-1 justify-between">
                    {/* Rating */}
                    <View className="flex-col gap-1">
                        <View className="flex-row items-center gap-1">
                            <Text className="text-yellow-500 text-sm">★</Text>
                            <Text className="text-neutral-500 text-xs font-medium uppercase">
                                {rating.toFixed(1)} ({total_reviews} avaliações)
                            </Text>
                        </View>

                        {/* Nome */}
                        <Text className="text-neutral-900 text-lg font-bold leading-tight">
                            {displayName}
                        </Text>

                        {/* Veículo + Categoria */}
                        <Text className="text-neutral-500 text-sm">
                            {vehicle_type} • Categoria {license_category}
                        </Text>
                    </View>

                    {/* Preço e botão */}
                    <View className="mt-3 flex-row items-center justify-between">
                        <View className="flex-row items-baseline gap-0.5">
                            <Text className="text-primary-600 text-sm font-bold">R$</Text>
                            <Text className="text-primary-600 text-xl font-bold">
                                {hourly_rate.toFixed(0)}
                            </Text>
                            <Text className="text-neutral-400 text-xs">/hora</Text>
                        </View>

                        <TouchableOpacity
                            onPress={() => onViewProfile(id)}
                            className="bg-primary-100 px-3 py-1.5 rounded-lg"
                            activeOpacity={0.7}
                        >
                            <Text className="text-primary-600 text-sm font-bold">Ver Perfil</Text>
                        </TouchableOpacity>
                    </View>
                </View>

                {/* Avatar à direita */}
                <View className="w-24 h-24 rounded-xl overflow-hidden bg-neutral-200">
                    {avatar_url ? (
                        <Image
                            source={{ uri: avatar_url }}
                            className="w-full h-full"
                            resizeMode="cover"
                        />
                    ) : (
                        <View className="w-full h-full items-center justify-center bg-primary-100">
                            <Text className="text-primary-600 text-2xl font-bold">
                                {displayName.charAt(0).toUpperCase()}
                            </Text>
                        </View>
                    )}
                </View>
            </View>
        </View>
    );
}

// Memoizar para evitar re-renders desnecessários em listas
export const InstructorCard = memo(InstructorCardComponent);
