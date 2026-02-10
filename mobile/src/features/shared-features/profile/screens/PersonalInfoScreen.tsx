/**
 * PersonalInfoScreen
 *
 * Tela de edição de informações pessoais do aluno.
 * Inclui campo de localização crítico para busca de instrutores.
 */

import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    ScrollView,
    TouchableOpacity,
    SafeAreaView,
    TextInput,
    ActivityIndicator,
    Alert,
    Platform,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import {
    ChevronLeft,
    MapPin,
    RefreshCw,
    ShieldCheck,
} from 'lucide-react-native';
import * as Location from 'expo-location';

import { useAuthStore, useLocationStore } from '../../../../lib/store';
import { useStudentProfile, useUpdateStudentProfile, useUpdateLocation } from '../hooks/useStudentProfile';
import { Button } from '../../../../shared/components';

// Componente de input customizado para esta tela
interface FormInputProps {
    label: string;
    value: string;
    onChangeText: (text: string) => void;
    placeholder?: string;
    keyboardType?: 'default' | 'phone-pad' | 'numeric';
    editable?: boolean;
}

function FormInput({
    label,
    value,
    onChangeText,
    placeholder,
    keyboardType = 'default',
    editable = true,
}: FormInputProps) {
    return (
        <View className="mb-4">
            <Text className="text-sm font-medium text-gray-600 mb-2">{label}</Text>
            <TextInput
                value={value}
                onChangeText={onChangeText}
                placeholder={placeholder}
                keyboardType={keyboardType}
                editable={editable}
                className={`
                    bg-gray-50 border border-gray-200 rounded-xl px-4 py-3.5
                    text-base text-gray-900
                    ${!editable ? 'opacity-60' : ''}
                `}
                placeholderTextColor="#9CA3AF"
            />
        </View>
    );
}

export function PersonalInfoScreen() {
    const navigation = useNavigation();
    const { user } = useAuthStore();
    const { latitude, longitude } = useLocationStore();

    // API hooks
    const { data: profile, isLoading: isLoadingProfile } = useStudentProfile();
    const updateProfile = useUpdateStudentProfile();
    const updateLocation = useUpdateLocation();

    // Form state
    const [name, setName] = useState(user?.full_name || '');
    const [phone, setPhone] = useState('');
    const [cpf, setCpf] = useState('');
    const [birthDate, setBirthDate] = useState('');

    // Location state
    const [locationAddress, setLocationAddress] = useState<string | null>(null);
    const [isLoadingLocation, setIsLoadingLocation] = useState(false);
    const [locationError, setLocationError] = useState<string | null>(null);

    // Carregar dados do perfil quando disponível
    useEffect(() => {
        if (profile) {
            setPhone(profile.phone || '');
            setCpf(profile.cpf || '');
            // Converter de ISO (YYYY-MM-DD) para formato BR (DD/MM/YYYY)
            if (profile.birth_date) {
                const [year, month, day] = profile.birth_date.split('-');
                setBirthDate(`${day}/${month}/${year}`);
            }
        }
    }, [profile]);

    // Carregar endereço quando coordenadas mudarem
    useEffect(() => {
        if (latitude && longitude) {
            reverseGeocode(latitude, longitude);
        }
    }, [latitude, longitude]);

    // Geocoding reverso para mostrar endereço legível
    const reverseGeocode = async (lat: number, lng: number) => {
        try {
            const [result] = await Location.reverseGeocodeAsync({
                latitude: lat,
                longitude: lng,
            });

            if (result) {
                const address = [
                    result.street,
                    result.streetNumber,
                    result.district,
                    result.city,
                    result.region,
                ].filter(Boolean).join(', ');

                setLocationAddress(address || `${lat.toFixed(6)}, ${lng.toFixed(6)}`);
            }
        } catch (error) {
            console.log('[PersonalInfoScreen] Geocoding error:', error);
            setLocationAddress(`${lat.toFixed(6)}, ${lng.toFixed(6)}`);
        }
    };

    // Atualizar localização do dispositivo
    const handleUpdateLocation = async () => {
        setIsLoadingLocation(true);
        setLocationError(null);

        try {
            // Solicitar permissão
            const { status } = await Location.requestForegroundPermissionsAsync();

            if (status !== 'granted') {
                setLocationError('Permissão de localização negada');
                Alert.alert(
                    'Permissão Necessária',
                    'Para atualizar sua localização, você precisa conceder permissão de acesso à localização nas configurações do dispositivo.',
                    [{ text: 'OK' }]
                );
                return;
            }

            // Obter localização atual
            const location = await Location.getCurrentPositionAsync({
                accuracy: Location.Accuracy.Balanced,
            });

            // Atualizar via hook (store + backend)
            await updateLocation.mutateAsync({
                latitude: location.coords.latitude,
                longitude: location.coords.longitude,
            });

            // Feedback visual
            Alert.alert('Sucesso', 'Localização atualizada com sucesso!');

        } catch (error) {
            console.error('[PersonalInfoScreen] Location error:', error);
            setLocationError('Erro ao obter localização');
            Alert.alert('Erro', 'Não foi possível obter sua localização. Tente novamente.');
        } finally {
            setIsLoadingLocation(false);
        }
    };

    // Converter data BR (DD/MM/YYYY) para ISO (YYYY-MM-DD)
    const convertDateToISO = (brDate: string): string | null => {
        if (!brDate || brDate.length < 10) return null;
        const parts = brDate.split('/');
        if (parts.length !== 3) return null;
        const [day, month, year] = parts;
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    };

    // Salvar dados do perfil
    const handleSave = async () => {
        try {
            // Converter data para formato ISO
            const isoDate = convertDateToISO(birthDate);

            await updateProfile.mutateAsync({
                full_name: name || undefined,
                phone: phone || undefined,
                cpf: cpf || undefined,
                birth_date: isoDate,
            });

            Alert.alert('Sucesso', 'Dados salvos com sucesso!');
            navigation.goBack();
        } catch (error) {
            console.error('[PersonalInfoScreen] Save error:', error);
            Alert.alert('Erro', 'Não foi possível salvar os dados. Tente novamente.');
        }
    };

    // Formatação de CPF
    const formatCPF = (text: string) => {
        const cleaned = text.replace(/\D/g, '').slice(0, 11);
        const match = cleaned.match(/^(\d{0,3})(\d{0,3})(\d{0,3})(\d{0,2})$/);
        if (match) {
            return [match[1], match[2], match[3]]
                .filter(Boolean)
                .join('.')
                .concat(match[4] ? `-${match[4]}` : '');
        }
        return text;
    };

    // Formatação de telefone
    const formatPhone = (text: string) => {
        const cleaned = text.replace(/\D/g, '').slice(0, 11);
        const match = cleaned.match(/^(\d{0,2})(\d{0,5})(\d{0,4})$/);
        if (match) {
            let result = '';
            if (match[1]) result = `(${match[1]}`;
            if (match[2]) result += `) ${match[2]}`;
            if (match[3]) result += `-${match[3]}`;
            return result;
        }
        return text;
    };

    // Formatação de data
    const formatDate = (text: string) => {
        const cleaned = text.replace(/\D/g, '').slice(0, 8);
        const match = cleaned.match(/^(\d{0,2})(\d{0,2})(\d{0,4})$/);
        if (match) {
            return [match[1], match[2], match[3]].filter(Boolean).join('/');
        }
        return text;
    };

    if (isLoadingProfile) {
        return (
            <SafeAreaView className="flex-1 bg-white items-center justify-center">
                <ActivityIndicator size="large" color="#2563EB" />
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
                    Informações Pessoais
                </Text>
                <View className="w-10" />
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerClassName="py-6"
                showsVerticalScrollIndicator={false}
                keyboardShouldPersistTaps="handled"
            >
                {/* Banner LGPD */}
                <View className="flex-row items-start bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
                    <ShieldCheck size={20} color="#16A34A" />
                    <View className="flex-1 ml-3">
                        <Text className="text-sm font-semibold text-green-800">
                            Seus dados estão protegidos
                        </Text>
                        <Text className="text-xs text-green-700 mt-1 leading-5">
                            Suas informações pessoais, exceto nome, não serão exibidas publicamente e estão
                            protegidas de acordo com a Lei Geral de Proteção de Dados (LGPD). Essas informações são usadas para validar sua identidade e garantir a segurança da plataforma.
                        </Text>
                    </View>
                </View>

                {/* Campos do formulário */}
                <FormInput
                    label="Nome Completo"
                    value={name}
                    onChangeText={setName}
                    placeholder="Seu nome"
                />

                <FormInput
                    label="Telefone"
                    value={phone}
                    onChangeText={(text) => setPhone(formatPhone(text))}
                    placeholder="(00) 00000-0000"
                    keyboardType="phone-pad"
                />

                <FormInput
                    label="CPF"
                    value={cpf}
                    onChangeText={(text) => setCpf(formatCPF(text))}
                    placeholder="000.000.000-00"
                    keyboardType="numeric"
                />

                <FormInput
                    label="Data de Nascimento"
                    value={birthDate}
                    onChangeText={(text) => setBirthDate(formatDate(text))}
                    placeholder="DD/MM/AAAA"
                    keyboardType="numeric"
                />

                {/* Seção de Localização */}
                <View className="mt-6 mb-4">
                    <Text className="text-sm font-medium text-gray-600 mb-2">
                        Localização
                    </Text>
                    <Text className="text-xs text-gray-400 mb-3">
                        Sua localização é usada para buscar instrutores próximos a você. Para sua segurança, o endereço não é compartilhado.
                    </Text>

                    <View className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                        <View className="flex-row items-start">
                            <MapPin size={20} color="#2563EB" />
                            <View className="flex-1 ml-3">
                                {latitude && longitude ? (
                                    <>
                                        <Text className="text-sm font-medium text-gray-900">
                                            {locationAddress || 'Buscando endereço...'}
                                        </Text>
                                        <Text className="text-xs text-gray-500 mt-1">
                                            Lat: {latitude.toFixed(6)}, Lng: {longitude.toFixed(6)}
                                        </Text>
                                    </>
                                ) : (
                                    <Text className="text-sm text-gray-500">
                                        Localização não definida
                                    </Text>
                                )}
                            </View>
                        </View>

                        {locationError && (
                            <Text className="text-xs text-red-500 mt-2">
                                {locationError}
                            </Text>
                        )}

                        <TouchableOpacity
                            onPress={handleUpdateLocation}
                            disabled={isLoadingLocation}
                            className={`
                                flex-row items-center justify-center mt-4 py-3 rounded-lg
                                ${isLoadingLocation ? 'bg-blue-100' : 'bg-blue-600 active:bg-blue-700'}
                            `}
                        >
                            {isLoadingLocation ? (
                                <ActivityIndicator size="small" color="#2563EB" />
                            ) : (
                                <>
                                    <RefreshCw size={16} color="#ffffff" />
                                    <Text className="ml-2 text-sm font-semibold text-white">
                                        Atualizar Localização
                                    </Text>
                                </>
                            )}
                        </TouchableOpacity>
                    </View>
                </View>
            </ScrollView>

            {/* Botão Salvar */}
            <View className="px-4 pb-8 pt-4 border-t border-gray-100">
                <TouchableOpacity
                    onPress={handleSave}
                    disabled={updateProfile.isPending}
                    className={`
                        py-4 rounded-xl items-center justify-center
                        ${updateProfile.isPending ? 'bg-blue-400' : 'bg-blue-600 active:bg-blue-700'}
                    `}
                >
                    {updateProfile.isPending ? (
                        <ActivityIndicator size="small" color="#ffffff" />
                    ) : (
                        <Text className="text-base font-semibold text-white">
                            Salvar
                        </Text>
                    )}
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
