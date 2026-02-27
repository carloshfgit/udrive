/**
 * GoDrive Mobile - InstructorCard Component
 *
 * Card de instrutor conforme design de referência.
 */

import React, { memo } from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import { Instructor } from '../api/searchApi';
import { formatPrice } from '../../../../shared';

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
        user_id,
        name,
        full_name,
        city,
        rating,
        total_reviews,
        vehicle_type,
        license_category,
        avatar_url,
        distance_km,
    } = instructor;

    // Fallback para nome se não vier da API
    // A busca retorna full_name, os detalhes retornam name
    const displayName = full_name || name || 'Instrutor';

    // Texto de localização (Distância + Cidade)
    const locationText = [
        city,
        distance_km !== null ? `${distance_km.toFixed(1)} km` : null
    ].filter(Boolean).join(' • ');

    // Preços no veículo do aluno
    const priceA = instructor.price_cat_a_student_vehicle;
    const priceB = instructor.price_cat_b_student_vehicle;

    const renderPrice = () => {
        if (license_category === 'AB') {
            return (
                <View className="mt-3 flex-row items-center gap-3">
                    <View className="flex-row items-baseline">
                        <Text className="text-neutral-400 text-[10px] font-bold mr-1">A:</Text>
                        <Text className="text-primary-600 text-lg font-bold">
                            {priceA ? formatPrice(priceA) : '---'}
                        </Text>
                        <Text className="text-neutral-400 text-[10px] ml-0.5">/h</Text>
                    </View>
                    <View className="w-[1px] h-4 bg-neutral-200" />
                    <View className="flex-row items-baseline">
                        <Text className="text-neutral-400 text-[10px] font-bold mr-1">B:</Text>
                        <Text className="text-primary-600 text-lg font-bold">
                            {priceB ? formatPrice(priceB) : '---'}
                        </Text>
                        <Text className="text-neutral-400 text-[10px] ml-0.5">/h</Text>
                    </View>
                </View>
            );
        }

        const price = license_category === 'A' ? priceA : priceB;
        return (
            <View className="mt-3 flex-row items-baseline gap-0.5">
                <Text className="text-primary-600 text-xl font-bold">
                    {price ? formatPrice(price) : '---'}
                </Text>
                <Text className="text-neutral-400 text-xs">/hora</Text>
            </View>
        );
    };

    return (
        <View className="mx-4 my-2">
            <TouchableOpacity
                onPress={() => onViewProfile(user_id)}
                activeOpacity={0.7}
                className="flex-row items-stretch justify-between gap-4 rounded-xl bg-white p-4 shadow-sm border border-neutral-100"
            >
                {/* Conteúdo à esquerda */}
                <View className="flex-1 justify-between pr-2">
                    {/* Rating */}
                    <View className="flex-col gap-1">
                        <View className="flex-row items-center gap-1">
                            <Text className="text-yellow-500 text-sm">★</Text>
                            <Text className="text-neutral-500 text-xs font-medium uppercase">
                                {rating.toFixed(1)} ({total_reviews} avaliações)
                            </Text>
                        </View>
                        {/* Nome */}
                        <Text className="text-neutral-900 text-lg font-bold leading-tight" numberOfLines={2}>
                            {displayName}
                        </Text>

                        {/* Veículo + Categoria */}
                        <Text className="text-neutral-500 text-sm" numberOfLines={1}>
                            {vehicle_type} • CNH {license_category}
                        </Text>

                        {/* Localização (Cidade e Distância) */}
                        {locationText ? (
                            <Text className="text-primary-500 text-xs font-medium">
                                📍 {locationText}
                            </Text>
                        ) : (
                            <View className="flex-row items-center gap-1 mt-1">
                                <Text className="text-amber-600 text-xs font-medium">
                                    ⚠️ Localização indisponível
                                </Text>
                            </View>
                        )}
                    </View>

                    {/* Preço renderizado dinamicamente */}
                    {renderPrice()}
                </View>

                {/* Coluna Direita: Avatar + Botão */}
                <View className="items-center justify-between gap-3">
                    {/* Avatar */}
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

                    {/* Botão Ver Perfil Centralizado */}
                    <View
                        className="bg-primary-100 px-3 py-2 rounded-lg w-24 items-center justify-center"
                    >
                        <Text className="text-primary-600 text-xs font-bold text-center">Ver Perfil</Text>
                    </View>
                </View>
            </TouchableOpacity>
        </View>
    );
}

// Memoizar para evitar re-renders desnecessários em listas
export const InstructorCard = memo(InstructorCardComponent);
