/**
 * GoDrive Mobile - ProfileHeader Component
 *
 * Header do perfil do instrutor com foto, nome, rating, categoria e preço.
 */

import React from 'react';
import { View, Text, Image } from 'react-native';
import { StarRating, Badge } from '../../../../shared/components';
import { formatPrice } from '../../../../shared';
import { InstructorDetail } from '../api/instructorApi';

interface ProfileHeaderProps {
    instructor: InstructorDetail;
}

/**
 * Header do perfil do instrutor exibindo:
 * - Foto grande (ou iniciais)
 * - Nome completo
 * - Rating com número de avaliações
 * - Badge de categoria CNH
 * - Badge de disponibilidade
 * - Preço por hora em destaque
 */
export function ProfileHeader({ instructor }: ProfileHeaderProps) {
    const {
        name,
        rating,
        total_reviews,
        license_category,
        is_available,
        avatar_url,
    } = instructor;

    // Extrair iniciais do nome para fallback
    const getInitials = (fullName: string) => {
        return fullName
            .split(' ')
            .map((n) => n[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    };

    return (
        <View className="items-center px-6 py-8 bg-gradient-to-b from-primary-50 to-white">
            {/* Foto do Instrutor */}
            <View className="w-32 h-32 rounded-full border-4 border-white shadow-lg overflow-hidden bg-primary-100">
                {avatar_url ? (
                    <Image
                        source={{ uri: avatar_url }}
                        className="w-full h-full"
                        resizeMode="cover"
                    />
                ) : (
                    <View className="w-full h-full items-center justify-center">
                        <Text className="text-4xl font-bold text-primary-600">
                            {getInitials(name)}
                        </Text>
                    </View>
                )}
            </View>

            {/* Nome */}
            <Text className="text-2xl font-bold text-gray-900 mt-4 text-center">
                {name}
            </Text>

            {/* Rating */}
            <View className="mt-2">
                <StarRating
                    rating={rating}
                    showCount
                    count={total_reviews}
                    size={16}
                />
            </View>

            {/* Badges */}
            <View className="flex-row items-center gap-2 mt-3">
                <Badge
                    label={`Categoria ${license_category}`}
                    variant="default"
                />
                <Badge
                    label={is_available ? 'Disponível' : 'Indisponível'}
                    variant={is_available ? 'success' : 'warning'}
                />
            </View>

        </View>
    );
}
