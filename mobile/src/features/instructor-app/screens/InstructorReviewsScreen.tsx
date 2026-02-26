/**
 * InstructorReviewsScreen
 *
 * Tela que exibe as avaliações e comentários recebidos pelo instrutor.
 */

import React from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
    ActivityIndicator,
    FlatList,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { ChevronLeft, Star } from 'lucide-react-native';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

import { useInstructorReviews } from '../hooks/useInstructorProfile';

export function InstructorReviewsScreen() {
    const navigation = useNavigation();
    const { data, isLoading, isError, refetch } = useInstructorReviews();

    const renderHeader = () => (
        <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
            <TouchableOpacity
                onPress={() => navigation.goBack()}
                className="p-2 -ml-2"
            >
                <ChevronLeft size={24} color="#1F2937" />
            </TouchableOpacity>
            <Text className="text-lg font-bold text-gray-900 ml-2">Minhas Avaliações</Text>
        </View>
    );

    const renderRatingHeader = () => {
        if (!data) return null;

        return (
            <View className="items-center py-8 bg-blue-50/30">
                <Text className="text-5xl font-bold text-gray-900">{data.rating.toFixed(1)}</Text>
                <View className="flex-row mt-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                            key={star}
                            size={24}
                            fill={star <= Math.round(data.rating) ? "#EAB308" : "transparent"}
                            color="#EAB308"
                            className="mx-0.5"
                        />
                    ))}
                </View>
                <Text className="text-gray-500 mt-2">
                    Baseado em {data.total_reviews} {data.total_reviews === 1 ? 'avaliação' : 'avaliações'}
                </Text>
            </View>
        );
    };

    if (isLoading) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                {renderHeader()}
                <View className="flex-1 items-center justify-center">
                    <ActivityIndicator size="large" color="#2563EB" />
                </View>
            </SafeAreaView>
        );
    }

    if (isError) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                {renderHeader()}
                <View className="flex-1 items-center justify-center p-6">
                    <Text className="text-lg font-semibold text-gray-900 text-center">
                        Erro ao carregar avaliações
                    </Text>
                    <TouchableOpacity
                        onPress={() => refetch()}
                        className="mt-4 bg-blue-600 px-6 py-2 rounded-full"
                    >
                        <Text className="text-white font-bold">Tentar Novamente</Text>
                    </TouchableOpacity>
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-white">
            {renderHeader()}

            <FlatList
                data={data?.reviews || []}
                keyExtractor={(item) => item.id}
                ListHeaderComponent={renderRatingHeader}
                contentContainerClassName="pb-8"
                ListEmptyComponent={
                    <View className="items-center justify-center p-12">
                        <Star size={48} color="#E5E7EB" />
                        <Text className="text-gray-400 mt-4 text-center">
                            Você ainda não recebeu nenhuma avaliação.
                        </Text>
                    </View>
                }
                renderItem={({ item }) => (
                    <View className="px-4 py-4 border-b border-gray-50">
                        <View className="flex-row justify-between items-start">
                            <Text className="font-bold text-gray-900 flex-1">{item.student_name}</Text>
                            <Text className="text-xs text-gray-400">
                                {format(new Date(item.created_at), "dd 'de' MMMM", { locale: ptBR })}
                            </Text>
                        </View>

                        <View className="flex-row mt-1 mb-2">
                            {[1, 2, 3, 4, 5].map((star) => (
                                <Star
                                    key={star}
                                    size={14}
                                    fill={star <= item.rating ? "#EAB308" : "transparent"}
                                    color="#EAB308"
                                    className="mr-0.5"
                                />
                            ))}
                        </View>

                        {item.comment ? (
                            <Text className="text-gray-600 leading-5">{item.comment}</Text>
                        ) : (
                            <Text className="text-gray-400 italic">Sem comentário</Text>
                        )}
                    </View>
                )}
            />
        </SafeAreaView>
    );
}
