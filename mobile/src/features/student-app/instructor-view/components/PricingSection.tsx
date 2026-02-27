/**
 * GoDrive Mobile - PricingSection Component
 *
 * Exibe a grade de preços do instrutor por categoria e tipo de veículo.
 */

import React from 'react';
import { View, Text } from 'react-native';
import { DollarSign, Car, User } from 'lucide-react-native';
import { formatPrice } from '../../../../shared';

interface PricingSectionProps {
    priceAInstructor?: number | null;
    priceAStudent?: number | null;
    priceBInstructor?: number | null;
    priceBStudent?: number | null;
    licenseCategory: string;
}

export function PricingSection({
    priceAInstructor,
    priceAStudent,
    priceBInstructor,
    priceBStudent,
    licenseCategory,
}: PricingSectionProps) {
    const showA = licenseCategory.includes('A');
    const showB = licenseCategory.includes('B');

    const PriceCard = ({ title, price, icon: Icon, colorClass, bgColorClass }: any) => (
        <View className={`${bgColorClass} rounded-xl p-3 flex-1 border border-gray-100`}>
            <View className="flex-row items-center gap-1.5 mb-1">
                {Icon && <Icon size={14} className={colorClass} />}
                <Text className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">
                    {title}
                </Text>
            </View>
            <Text className={`text-base font-bold ${colorClass}`}>
                {price ? formatPrice(price) : '---'}
            </Text>
        </View>
    );

    return (
        <View className="px-6 py-4">
            {/* Título da Seção */}
            <View className="flex-row items-center gap-2 mb-4">
                <DollarSign size={20} color="#2563EB" />
                <Text className="text-lg font-semibold text-gray-900">
                    Valores das Aulas
                </Text>
            </View>

            <View className="gap-4">
                {/* Seção Veículo do Instrutor */}
                <View>
                    <View className="flex-row items-center gap-2 mb-2">
                        <Car size={16} color="#4B5563" />
                        <Text className="text-sm font-bold text-gray-700">No veículo do instrutor</Text>
                    </View>
                    <View className="flex-row gap-3">
                        {showA && (
                            <PriceCard
                                title="Moto (A)"
                                price={priceAInstructor}
                                colorClass="text-blue-600"
                                bgColorClass="bg-blue-50/50"
                            />
                        )}
                        {showB && (
                            <PriceCard
                                title="Carro (B)"
                                price={priceBInstructor}
                                colorClass="text-blue-600"
                                bgColorClass="bg-blue-50/50"
                            />
                        )}
                    </View>
                </View>

                {/* Seção Veículo do Aluno */}
                <View>
                    <View className="flex-row items-center gap-2 mb-2">
                        <User size={16} color="#4B5563" />
                        <Text className="text-sm font-bold text-gray-700">No seu veículo (aluno)</Text>
                    </View>
                    <View className="flex-row gap-3">
                        {showA && (
                            <PriceCard
                                title="Moto (A)"
                                price={priceAStudent}
                                colorClass="text-emerald-600"
                                bgColorClass="bg-emerald-50/50"
                            />
                        )}
                        {showB && (
                            <PriceCard
                                title="Carro (B)"
                                price={priceBStudent}
                                colorClass="text-emerald-600"
                                bgColorClass="bg-emerald-50/50"
                            />
                        )}
                    </View>
                </View>
            </View>
        </View>
    );
}
