import React, { useState } from 'react';
import {
    View,
    Text,
    SafeAreaView,
    ScrollView,
    TextInput,
    TouchableOpacity,
    Alert,
    KeyboardAvoidingView,
    Platform,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { AlertTriangle, Phone, Mail, ChevronRight } from 'lucide-react-native';
import { Header } from '../../../../shared/components/Header';
import { Button } from '../../../../shared/components/Button';
import { useAuth } from '../../../auth/hooks/useAuth';
import { useLessonDetails } from '../../../shared-features/scheduling/hooks/useLessonDetails';
import type { OpenDisputeData } from '../../../shared-features/scheduling/api/schedulingApi';

const REASONS = [
    { value: 'no_show' as const, label: 'Instrutor não compareceu', emoji: '🚫' },
    { value: 'vehicle_problem' as const, label: 'Problemas mecânicos no veículo', emoji: '🚗' },
    { value: 'other' as const, label: 'Outro motivo', emoji: '📝' },
];

export function ReportProblemScreen() {
    const route = useRoute<any>();
    const navigation = useNavigation<any>();
    const { schedulingId } = route.params;
    const { user } = useAuth();
    const { openDispute, isOpeningDispute } = useLessonDetails(schedulingId);

    const [selectedReason, setSelectedReason] = useState<OpenDisputeData['reason'] | null>(null);
    const [description, setDescription] = useState('');
    const [contactPhone, setContactPhone] = useState('');
    const [contactEmail, setContactEmail] = useState(user?.email || '');

    const isFormValid =
        selectedReason !== null &&
        description.trim().length >= 10 &&
        contactPhone.trim().length >= 8 &&
        contactEmail.trim().includes('@');

    const handleSubmit = async () => {
        if (!isFormValid || !selectedReason) return;

        try {
            await openDispute({
                reason: selectedReason,
                description: description.trim(),
                contact_phone: contactPhone.trim(),
                contact_email: contactEmail.trim(),
            });

            Alert.alert(
                'Relato Enviado',
                'Seu problema foi registrado com sucesso. O suporte entrará em contato em até 24 horas úteis.',
                [{ text: 'OK', onPress: () => navigation.goBack() }]
            );
        } catch (error: any) {
            const errorMessage =
                error.response?.data?.detail ||
                error.message ||
                'Não foi possível enviar o relato. Tente novamente.';
            Alert.alert('Erro', errorMessage);
        }
    };

    return (
        <SafeAreaView className="flex-1 bg-white">
            <Header title="Relatar Problema" onBack={() => navigation.goBack()} />

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                className="flex-1"
            >
                <ScrollView
                    className="flex-1 px-6 pt-4"
                    showsVerticalScrollIndicator={false}
                    keyboardShouldPersistTaps="handled"
                >
                    {/* Aviso Amigável */}
                    <View className="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-8">
                        <View className="flex-row items-center mb-3">
                            <View className="bg-amber-100 p-2 rounded-xl mr-3">
                                <AlertTriangle size={20} color="#D97706" />
                            </View>
                            <Text className="text-amber-800 font-bold text-base flex-1">
                                Está tendo problemas?
                            </Text>
                        </View>
                        <Text className="text-amber-700 text-sm leading-5">
                            Acumule evidências, fotos, prints, vídeos e solicite contato
                            com o suporte para resolver a situação.
                        </Text>
                    </View>

                    {/* Seleção de Motivo */}
                    <Text className="text-neutral-900 font-black text-lg mb-4">
                        Qual o motivo?
                    </Text>

                    <View className="gap-3 mb-8">
                        {REASONS.map((reason) => (
                            <TouchableOpacity
                                key={reason.value}
                                onPress={() => setSelectedReason(reason.value)}
                                className={`flex-row items-center p-4 rounded-2xl border-2 ${selectedReason === reason.value
                                    ? 'border-primary-500 bg-primary-50'
                                    : 'border-neutral-100 bg-neutral-50'
                                    }`}
                            >
                                <Text className="text-2xl mr-4">{reason.emoji}</Text>
                                <Text
                                    className={`flex-1 font-semibold text-base ${selectedReason === reason.value
                                        ? 'text-primary-700'
                                        : 'text-neutral-700'
                                        }`}
                                >
                                    {reason.label}
                                </Text>
                                {selectedReason === reason.value && (
                                    <View className="bg-primary-500 w-6 h-6 rounded-full items-center justify-center">
                                        <Text className="text-white text-xs font-bold">✓</Text>
                                    </View>
                                )}
                            </TouchableOpacity>
                        ))}
                    </View>

                    {/* Descrição */}
                    <Text className="text-neutral-900 font-black text-lg mb-3">
                        Descreva o ocorrido
                    </Text>
                    <TextInput
                        className="bg-neutral-50 border border-neutral-200 rounded-2xl p-4 text-neutral-900 text-base mb-2"
                        placeholder="Conte com detalhes o que aconteceu (mínimo 10 caracteres)..."
                        placeholderTextColor="#9CA3AF"
                        multiline
                        numberOfLines={4}
                        textAlignVertical="top"
                        value={description}
                        onChangeText={setDescription}
                        style={{ minHeight: 120 }}
                    />
                    <Text className="text-neutral-400 text-xs mb-8 ml-1">
                        {description.length}/2000 caracteres
                    </Text>

                    {/* Dados de Contato */}
                    <Text className="text-neutral-900 font-black text-lg mb-4">
                        Dados para contato
                    </Text>

                    <View className="mb-4">
                        <View className="flex-row items-center bg-neutral-50 border border-neutral-200 rounded-2xl px-4">
                            <Phone size={18} color="#9CA3AF" />
                            <TextInput
                                className="flex-1 p-4 text-neutral-900 text-base"
                                placeholder="Telefone"
                                placeholderTextColor="#9CA3AF"
                                value={contactPhone}
                                onChangeText={setContactPhone}
                                keyboardType="phone-pad"
                            />
                        </View>
                    </View>

                    <View className="mb-8">
                        <View className="flex-row items-center bg-neutral-50 border border-neutral-200 rounded-2xl px-4">
                            <Mail size={18} color="#9CA3AF" />
                            <TextInput
                                className="flex-1 p-4 text-neutral-900 text-base"
                                placeholder="E-mail"
                                placeholderTextColor="#9CA3AF"
                                value={contactEmail}
                                onChangeText={setContactEmail}
                                keyboardType="email-address"
                                autoCapitalize="none"
                            />
                        </View>
                    </View>

                    {/* Botão de Envio */}
                    <View className="mb-10">
                        <Button
                            title="Enviar Relato"
                            onPress={handleSubmit}
                            loading={isOpeningDispute}
                            disabled={!isFormValid}
                            size="lg"
                            fullWidth
                            variant={isFormValid ? 'primary' : 'ghost'}
                        />
                    </View>
                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
