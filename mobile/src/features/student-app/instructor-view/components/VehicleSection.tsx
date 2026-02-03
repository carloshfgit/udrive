/**
 * GoDrive Mobile - VehicleSection Component
 *
 * Seção "Veículo" exibindo informações sobre o veículo do instrutor.
 */

import React from 'react';
import { View, Text } from 'react-native';
import { Car } from 'lucide-react-native';
import { Badge } from '../../../../shared/components';

interface VehicleSectionProps {
    vehicleType: string;
    licenseCategory: string;
}

/**
 * Seção "Veículo" com tipo de veículo e categoria CNH.
 */
export function VehicleSection({ vehicleType, licenseCategory }: VehicleSectionProps) {
    if (!vehicleType || vehicleType.trim() === '') {
        return null;
    }

    return (
        <View className="px-6 py-4">
            {/* Título da Seção */}
            <View className="flex-row items-center gap-2 mb-3">
                <Car size={20} color="#2563EB" />
                <Text className="text-lg font-semibold text-gray-900">
                    Veículo
                </Text>
            </View>

            {/* Conteúdo */}
            <View className="bg-gray-50 rounded-xl p-4">
                <View className="flex-row items-center justify-between">
                    <View>
                        <Text className="text-sm text-gray-500 mb-1">
                            Tipo de veículo
                        </Text>
                        <Text className="text-base font-medium text-gray-900">
                            {vehicleType}
                        </Text>
                    </View>
                    <Badge
                        label={`CNH ${licenseCategory}`}
                        variant="info"
                    />
                </View>
            </View>
        </View>
    );
}
