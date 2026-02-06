import React, { useState } from 'react';
import { View, Text, Modal, TouchableOpacity, TextInput, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { X, Star } from 'lucide-react-native';
import { Button } from '../../../../shared/components/Button';
import { BookingResponse, createReview } from '../../../shared-features/scheduling/api/schedulingApi';

interface LessonEvaluationModalProps {
    visible: boolean;
    onClose: () => void;
    scheduling: BookingResponse | null;
    onSuccess: () => void;
}

export function LessonEvaluationModal({ visible, onClose, scheduling, onSuccess }: LessonEvaluationModalProps) {
    const [rating, setRating] = useState(0);
    const [comment, setComment] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async () => {
        if (!scheduling) return;
        if (rating === 0) {
            setError('Por favor, selecione uma nota.');
            return;
        }

        setIsSubmitting(true);
        setError(null);

        try {
            await createReview(scheduling.id, rating, comment);
            onSuccess();
            handleClose();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Não foi possível enviar a avaliação.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleClose = () => {
        setRating(0);
        setComment('');
        setError(null);
        onClose();
    };

    if (!scheduling) return null;

    return (
        <Modal
            visible={visible}
            animationType="slide"
            transparent={true}
            onRequestClose={handleClose}
        >
            <View className="flex-1 justify-end bg-black/50">
                <KeyboardAvoidingView
                    behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                >
                    <View className="bg-white rounded-t-[40px] px-6 pt-8 pb-10">
                        {/* Header */}
                        <View className="flex-row justify-between items-center mb-6">
                            <View>
                                <Text className="text-neutral-900 font-bold text-2xl">Avaliar Aula</Text>
                                <Text className="text-neutral-500 text-sm">{scheduling.instructor_name}</Text>
                            </View>
                            <TouchableOpacity
                                onPress={handleClose}
                                className="bg-neutral-100 p-2 rounded-full"
                            >
                                <X size={20} color="#6B7280" />
                            </TouchableOpacity>
                        </View>

                        <ScrollView showsVerticalScrollIndicator={false}>
                            {/* Star Selection */}
                            <Text className="text-neutral-700 font-semibold mb-3 text-center">Como foi sua experiência?</Text>
                            <View className="flex-row justify-center space-x-2 mb-8">
                                {[1, 2, 3, 4, 5].map((star) => (
                                    <TouchableOpacity
                                        key={star}
                                        onPress={() => {
                                            setRating(star);
                                            setError(null);
                                        }}
                                        activeOpacity={0.7}
                                    >
                                        <Star
                                            size={48}
                                            fill={star <= rating ? "#EAB308" : "transparent"}
                                            color={star <= rating ? "#EAB308" : "#D1D5DB"}
                                        />
                                    </TouchableOpacity>
                                ))}
                            </View>

                            {/* Comment Input */}
                            <View>
                                <Text className="text-neutral-700 font-semibold mb-2">Comentário (opcional)</Text>
                                <TextInput
                                    className="bg-neutral-50 border border-neutral-200 rounded-2xl p-4 text-neutral-900 text-base min-h-[120px]"
                                    placeholder="Conte um pouco como foi a aula..."
                                    placeholderTextColor="#9CA3AF"
                                    multiline
                                    textAlignVertical="top"
                                    value={comment}
                                    onChangeText={setComment}
                                />
                            </View>

                            {error && (
                                <Text className="text-error-500 text-sm mt-3 text-center font-medium">{error}</Text>
                            )}

                            {/* Action Buttons */}
                            <View className="flex-row space-x-3 mt-8">
                                <View className="flex-1">
                                    <Button
                                        title="Cancelar"
                                        variant="outline"
                                        onPress={handleClose}
                                        disabled={isSubmitting}
                                    />
                                </View>
                                <View className="flex-1">
                                    <Button
                                        title="Enviar"
                                        onPress={handleSubmit}
                                        loading={isSubmitting}
                                    />
                                </View>
                            </View>
                        </ScrollView>
                    </View>
                </KeyboardAvoidingView>
            </View>
        </Modal>
    );
}
