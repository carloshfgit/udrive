/**
 * GoDrive Mobile - MapView Component
 *
 * Placeholder para visualização de instrutores em mapa.
 * Será integrado com react-native-maps na etapa M2.3.
 */

import React from 'react';
import { View, Text } from 'react-native';

interface MapViewProps {
    className?: string;
}

/**
 * Placeholder para o mapa de instrutores.
 * A integração completa com react-native-maps será feita na etapa M2.3.
 */
export function MapView({ className = '' }: MapViewProps) {
    return (
        <View className={`flex-1 items-center justify-center bg-neutral-100 ${className}`}>
            <View className="items-center p-8">
                <Text className="text-4xl mb-4">🗺️</Text>
                <Text className="text-neutral-900 text-lg font-semibold text-center">
                    Visualização em Mapa
                </Text>
                <Text className="text-neutral-500 text-sm text-center mt-2">
                    Em breve: veja instrutores próximos no mapa
                </Text>
            </View>
        </View>
    );
}
