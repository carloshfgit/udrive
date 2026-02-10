/**
 * GoDrive Mobile - ReviewsSection Component
 *
 * Seção que exibe as avaliações dos alunos sobre o instrutor.
 * Exibe apenas um comentário por aluno (o primeiro).
 */

import React from 'react';
import { View, Text } from 'react-native';
import { StarRating } from '../../../../shared/components';
import { PublicReview } from '../api/instructorApi';

interface ReviewsSectionProps {
    reviews: PublicReview[];
}

export function ReviewsSection({ reviews }: ReviewsSectionProps) {
    if (!reviews || reviews.length === 0) return null;

    return (
        <View className="px-6 py-6 border-t border-gray-100 bg-white">
            <Text className="text-xl font-bold text-gray-900 mb-4">
                Avaliações de Alunos
            </Text>

            <View className="gap-y-4">
                {reviews.map((review, index) => (
                    <View
                        key={`${review.student_name}-${index}`}
                        className="bg-gray-50 p-4 rounded-xl border border-gray-100 shadow-sm"
                    >
                        <View className="flex-row items-center justify-between mb-2">
                            <Text className="font-semibold text-gray-900">
                                {review.student_name}
                            </Text>
                            <Text className="text-xs text-gray-500">
                                {new Date(review.created_at).toLocaleDateString('pt-BR')}
                            </Text>
                        </View>

                        <StarRating
                            rating={review.rating}
                            size={12}
                            className="mb-2"
                        />

                        {review.comment && (
                            <Text className="text-gray-600 text-sm leading-5 mt-1">
                                "{review.comment}"
                            </Text>
                        )}
                    </View>
                ))}
            </View>
        </View>
    );
}
