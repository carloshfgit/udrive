/**
 * GoDrive Mobile - AboutSection Component
 *
 * Seção "Sobre" exibindo a biografia do instrutor.
 */

import React from 'react';
import { View, Text } from 'react-native';
import { FileText } from 'lucide-react-native';

interface AboutSectionProps {
    bio: string;
}

/**
 * Seção "Sobre" com a biografia do instrutor.
 */
export function AboutSection({ bio }: AboutSectionProps) {
    if (!bio || bio.trim() === '') {
        return null;
    }

    return (
        <View className="px-6 py-4">
            {/* Título da Seção */}
            <View className="flex-row items-center gap-2 mb-3">
                <FileText size={20} color="#2563EB" />
                <Text className="text-lg font-semibold text-gray-900">
                    Sobre
                </Text>
            </View>

            {/* Conteúdo */}
            <View className="bg-gray-50 rounded-xl p-4">
                <Text className="text-base text-gray-700 leading-relaxed">
                    {bio}
                </Text>
            </View>
        </View>
    );
}
