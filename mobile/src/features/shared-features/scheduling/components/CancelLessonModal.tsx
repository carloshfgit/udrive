/**
 * GoDrive Mobile - CancelLessonModal Component
 *
 * Modal de confirmação de cancelamento de aula com exibição
 * do percentual de reembolso aplicável. Sem campo de motivo.
 */

import React, { useMemo } from 'react';
import { View, Text } from 'react-native';
import { AlertTriangle, Clock, ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react-native';
import { BottomSheet } from '../../../../shared/components/BottomSheet';
import { Button } from '../../../../shared/components/Button';
import { formatPrice } from '../../../../shared';

interface CancelLessonModalProps {
    isVisible: boolean;
    onClose: () => void;
    onConfirm: () => void;
    isSubmitting?: boolean;
    scheduledDatetime: string;
    price: number;
    isInstructor?: boolean;
}

/**
 * Calcula o percentual de reembolso com base na antecedência.
 * Regras:
 *   - >= 48h: 100%
 *   - 24-48h: 50%
 *   - < 24h: 0%
 *   - Instrutor cancela: sempre 100%
 */
function calculateRefundInfo(scheduledDatetime: string, isInstructor: boolean) {
    if (isInstructor) {
        return { percentage: 100, tier: 'full' as const };
    }

    const now = Date.now();
    const lessonTime = new Date(scheduledDatetime).getTime();
    const diffHours = (lessonTime - now) / 3_600_000;

    if (diffHours >= 48) return { percentage: 100, tier: 'full' as const };
    if (diffHours >= 24) return { percentage: 50, tier: 'partial' as const };
    return { percentage: 0, tier: 'none' as const };
}

export function CancelLessonModal({
    isVisible,
    onClose,
    onConfirm,
    isSubmitting = false,
    scheduledDatetime,
    price,
    isInstructor = false,
}: CancelLessonModalProps) {
    const { percentage, tier } = useMemo(
        () => calculateRefundInfo(scheduledDatetime, isInstructor),
        [scheduledDatetime, isInstructor],
    );

    const refundAmount = (price * percentage) / 100;

    // Visual configs por tier
    const tierConfig = {
        full: {
            icon: <ShieldCheck size={32} color="#16A34A" />,
            bgColor: 'bg-green-50',
            borderColor: 'border-green-200',
            textColor: 'text-green-700',
            percentColor: 'text-green-600',
            label: 'Reembolso Integral',
            description: isInstructor
                ? 'Como instrutor, o aluno receberá reembolso integral (100%).'
                : 'Você receberá o valor total de volta.',
        },
        partial: {
            icon: <ShieldAlert size={32} color="#D97706" />,
            bgColor: 'bg-amber-50',
            borderColor: 'border-amber-200',
            textColor: 'text-amber-700',
            percentColor: 'text-amber-600',
            label: 'Reembolso Parcial',
            description: 'Faltam entre 24h e 48h para a aula. 50% será retido como taxa de reserva. Considere reagendar gratuitamente.',
        },
        none: {
            icon: <ShieldX size={32} color="#DC2626" />,
            bgColor: 'bg-red-50',
            borderColor: 'border-red-200',
            textColor: 'text-red-700',
            percentColor: 'text-red-600',
            label: 'Sem Reembolso',
            description: 'Faltam menos de 24h para a aula. Não há direito a reembolso. Considere reagendar gratuitamente.',
        },
    };

    const config = tierConfig[tier];

    return (
        <BottomSheet
            isVisible={isVisible}
            onClose={onClose}
            title="Cancelar Aula"
        >
            <View className="pb-6">
                {/* Ícone de alerta */}
                <View className="items-center mb-5">
                    <View className="bg-red-50 p-4 rounded-full mb-3">
                        <AlertTriangle size={28} color="#DC2626" />
                    </View>
                    <Text className="text-neutral-900 font-bold text-lg text-center">
                        Deseja cancelar esta aula?
                    </Text>
                    <Text className="text-neutral-500 text-sm text-center mt-1">
                        Esta ação não pode ser desfeita.
                    </Text>
                </View>

                {/* Card de Reembolso */}
                <View
                    className={`${config.bgColor} ${config.borderColor} border rounded-2xl p-5 mb-6`}
                >
                    <View className="flex-row items-center mb-3">
                        {config.icon}
                        <View className="ml-3 flex-1">
                            <Text className={`${config.textColor} font-black text-xs uppercase tracking-widest`}>
                                {config.label}
                            </Text>
                        </View>
                    </View>

                    {/* Percentual e valor */}
                    <View className="flex-row items-baseline mb-3">
                        <Text className={`${config.percentColor} font-black text-4xl`}>
                            {percentage}%
                        </Text>
                        {percentage > 0 && (
                            <Text className={`${config.textColor} text-sm ml-2`}>
                                ({formatPrice(refundAmount)} de volta)
                            </Text>
                        )}
                    </View>

                    <Text className={`${config.textColor} text-sm leading-5`}>
                        {config.description}
                    </Text>
                </View>

                {/* Info de horário */}
                <View className="flex-row items-center bg-neutral-50 rounded-xl p-3 mb-6 border border-neutral-100">
                    <Clock size={16} color="#9CA3AF" />
                    <Text className="text-neutral-500 text-xs ml-2 flex-1">
                        Aula agendada para{' '}
                        <Text className="font-bold text-neutral-700">
                            {new Date(scheduledDatetime).toLocaleDateString('pt-BR', {
                                day: '2-digit',
                                month: 'long',
                            })}
                        </Text>{' '}
                        às{' '}
                        <Text className="font-bold text-neutral-700">
                            {new Date(scheduledDatetime).toLocaleTimeString('pt-BR', {
                                hour: '2-digit',
                                minute: '2-digit',
                            })}
                        </Text>
                    </Text>
                </View>

                {/* Botões */}
                <View className="flex-row gap-3">
                    <Button
                        title="Manter Aula"
                        variant="outline"
                        className="flex-1"
                        onPress={onClose}
                        disabled={isSubmitting}
                    />
                    <Button
                        title="Confirmar Cancelamento"
                        variant="danger"
                        className="flex-1"
                        onPress={onConfirm}
                        loading={isSubmitting}
                        disabled={isSubmitting}
                    />
                </View>
            </View>
        </BottomSheet>
    );
}
