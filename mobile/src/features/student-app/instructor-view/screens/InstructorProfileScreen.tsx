/**
 * GoDrive Mobile - InstructorProfileScreen
 *
 * Tela de visualização do perfil completo de um instrutor pelo aluno.
 * Exibe informações profissionais derivadas de EditInstructorProfileScreen.
 */

import React from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
    ActivityIndicator,
    Alert,
} from 'react-native';
import { useNavigation, useRoute, RouteProp } from '@react-navigation/native';
import { ChevronLeft, Calendar } from 'lucide-react-native';

import { useInstructorProfile } from '../hooks/useInstructorProfile';
import { ProfileHeader, AboutSection, VehicleSection } from '../components';
import { EmptyState } from '../../../../shared/components';

// Tipo para as rotas
type InstructorProfileRouteParams = {
    InstructorProfile: {
        instructorId: string;
    };
};

export function InstructorProfileScreen() {
    const navigation = useNavigation();
    const route = useRoute<RouteProp<InstructorProfileRouteParams, 'InstructorProfile'>>();
    const { instructorId } = route.params;

    // Buscar dados do instrutor
    const { data: instructor, isLoading, isError, refetch } = useInstructorProfile(instructorId);

    // Handler para agendar aula (placeholder para M3.2)
    const handleScheduleLesson = () => {
        Alert.alert(
            'Em breve',
            'A funcionalidade de agendamento será implementada na próxima etapa.',
            [{ text: 'OK' }]
        );
    };

    // Estado de loading
    if (isLoading) {
        return (
            <SafeAreaView className="flex-1 bg-white items-center justify-center">
                <ActivityIndicator size="large" color="#2563EB" />
                <Text className="text-gray-500 mt-4">Carregando perfil...</Text>
            </SafeAreaView>
        );
    }

    // Estado de erro
    if (isError || !instructor) {
        return (
            <SafeAreaView className="flex-1 bg-white">
                {/* Header */}
                <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
                    <TouchableOpacity
                        onPress={() => navigation.goBack()}
                        className="w-10 h-10 items-center justify-center"
                        accessibilityLabel="Voltar"
                    >
                        <ChevronLeft size={24} color="#111318" />
                    </TouchableOpacity>
                    <Text className="flex-1 text-lg font-bold text-gray-900 text-center">
                        Perfil do Instrutor
                    </Text>
                    <View className="w-10" />
                </View>

                <View className="flex-1 items-center justify-center px-6">
                    <EmptyState
                        title="Erro ao carregar"
                        message="Não foi possível carregar os dados do instrutor."
                        action={
                            <TouchableOpacity
                                onPress={() => refetch()}
                                className="bg-primary-600 px-6 py-3 rounded-xl"
                            >
                                <Text className="text-white font-semibold">
                                    Tentar novamente
                                </Text>
                            </TouchableOpacity>
                        }
                    />
                </View>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-white">
            {/* Header */}
            <View className="flex-row items-center px-4 py-3 border-b border-gray-100">
                <TouchableOpacity
                    onPress={() => navigation.goBack()}
                    className="w-10 h-10 items-center justify-center"
                    accessibilityLabel="Voltar"
                >
                    <ChevronLeft size={24} color="#111318" />
                </TouchableOpacity>
                <Text className="flex-1 text-lg font-bold text-gray-900 text-center">
                    Perfil do Instrutor
                </Text>
                <View className="w-10" />
            </View>

            {/* Conteúdo */}
            <ScrollView
                className="flex-1"
                showsVerticalScrollIndicator={false}
            >
                {/* Header do Perfil */}
                <ProfileHeader instructor={instructor} />

                {/* Seção Sobre */}
                <AboutSection bio={instructor.bio} />

                {/* Seção Veículo */}
                <VehicleSection
                    vehicleType={instructor.vehicle_type}
                    licenseCategory={instructor.license_category}
                />

                {/* Espaço para o botão fixo */}
                <View className="h-24" />
            </ScrollView>

            {/* Botão Fixo - Agendar Aula */}
            <View className="absolute bottom-0 left-0 right-0 px-6 pb-8 pt-4 bg-white border-t border-gray-100">
                <TouchableOpacity
                    onPress={handleScheduleLesson}
                    className="flex-row items-center justify-center py-4 rounded-xl bg-primary-600 active:bg-primary-700"
                    accessibilityLabel="Agendar Aula"
                >
                    <Calendar size={20} color="#ffffff" />
                    <Text className="text-base font-semibold text-white ml-2">
                        Agendar Aula
                    </Text>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
