/**
 * EditPublicProfileScreen
 *
 * Tela de edição do perfil público do instrutor.
 * Contém dados visíveis na busca: foto, bio, tipo de veículo, categoria CNH,
 * valor hora/aula, disponibilidade e localização.
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
    Switch,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import {
    ChevronLeft,
    Camera,
    DollarSign,
    MapPin,
    RefreshCw,
    Lightbulb,
} from 'lucide-react-native';
import * as Location from 'expo-location';

import { useAuthStore, useLocationStore } from '../../../lib/store';
import { useInstructorProfile, useUpdateInstructorProfile } from '../hooks/useInstructorProfile';
import { Avatar } from '../../../shared/components';

// Categorias de CNH disponíveis
const CNH_CATEGORIES = ['A', 'B', 'AB', 'C', 'D', 'E'];

// Componente de input customizado
interface FormInputProps {
    label: string;
    value: string;
    onChangeText: (text: string) => void;
    placeholder?: string;
    keyboardType?: 'default' | 'numeric' | 'decimal-pad' | 'phone-pad';
    multiline?: boolean;
    numberOfLines?: number;
    maxLength?: number;
    leftIcon?: React.ReactNode;
    editable?: boolean;
}

function FormInput({
    label,
    value,
    onChangeText,
    placeholder,
    keyboardType = 'default',
    multiline = false,
    numberOfLines = 1,
    maxLength,
    leftIcon,
    editable = true,
}: FormInputProps) {
    return (
        <View className="mb-4">
            <Text className="text-sm font-medium text-gray-600 mb-2">{label}</Text>
            <View className={`flex-row items-start bg-gray-50 border border-gray-200 rounded-xl overflow-hidden ${!editable ? 'opacity-60' : ''}`}>
                {leftIcon && (
                    <View className="pl-4 py-4 justify-center items-center">
                        {leftIcon}
                    </View>
                )}
                <TextInput
                    value={value}
                    onChangeText={onChangeText}
                    placeholder={placeholder}
                    keyboardType={keyboardType}
                    multiline={multiline}
                    numberOfLines={numberOfLines}
                    maxLength={maxLength}
                    editable={editable}
                    textAlignVertical={multiline ? 'top' : 'center'}
                    className={`
                        flex-1 text-base text-gray-900 px-4 py-3.5
                        ${multiline ? 'min-h-[100px]' : ''}
                        ${leftIcon ? 'pl-2' : ''}
                    `}
                    placeholderTextColor="#9CA3AF"
                />
            </View>
            {maxLength && (
                <Text className="text-xs text-gray-400 text-right mt-1">
                    {value.length}/{maxLength}
                </Text>
            )}
        </View>
    );
}

// Componente de seleção de categoria CNH
interface CNHSelectorProps {
    selected: string;
    onSelect: (category: string) => void;
}

function CNHSelector({ selected, onSelect }: CNHSelectorProps) {
    return (
        <View className="mb-4">
            <Text className="text-sm font-medium text-gray-600 mb-2">
                Categoria da CNH
            </Text>
            <View className="flex-row flex-wrap gap-2">
                {CNH_CATEGORIES.map((category) => {
                    const isSelected = selected === category;
                    return (
                        <TouchableOpacity
                            key={category}
                            onPress={() => onSelect(category)}
                            className={`
                                px-4 py-2.5 rounded-xl border-2
                                ${isSelected
                                    ? 'bg-blue-600 border-blue-600'
                                    : 'bg-white border-gray-200'
                                }
                            `}
                        >
                            <Text
                                className={`
                                    text-base font-semibold
                                    ${isSelected ? 'text-white' : 'text-gray-700'}
                                `}
                            >
                                {category}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </View>
        </View>
    );
}

export function EditPublicProfileScreen() {
    const navigation = useNavigation();
    const { user } = useAuthStore();
    const { latitude, longitude, setLocation } = useLocationStore();

    // API hooks
    const { data: profile, isLoading: isLoadingProfile } = useInstructorProfile();
    const updateProfile = useUpdateInstructorProfile();

    // Dados do perfil público
    const [bio, setBio] = useState('');
    const [vehicleType, setVehicleType] = useState('');
    const [licenseCategory, setLicenseCategory] = useState('B');
    const [hourlyRate, setHourlyRate] = useState('');
    const [isAvailable, setIsAvailable] = useState(true);

    // Location state
    const [locationAddress, setLocationAddress] = useState<string | null>(null);
    const [isLoadingLocation, setIsLoadingLocation] = useState(false);
    const [locationError, setLocationError] = useState<string | null>(null);

    // Carregar dados do perfil quando disponível
    useEffect(() => {
        if (profile) {
            setBio(profile.bio || '');
            setVehicleType(profile.vehicle_type || '');
            setLicenseCategory(profile.license_category || 'B');
            setHourlyRate(profile.hourly_rate?.toString() || '80');
            setIsAvailable(profile.is_available ?? true);
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
            console.log('[EditPublicProfileScreen] Geocoding error:', error);
            setLocationAddress(`${lat.toFixed(6)}, ${lng.toFixed(6)}`);
        }
    };

    // Atualizar localização do dispositivo
    const handleUpdateLocation = async () => {
        setIsLoadingLocation(true);
        setLocationError(null);

        try {
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

            const location = await Location.getCurrentPositionAsync({
                accuracy: Location.Accuracy.Balanced,
            });

            setLocation(location.coords.latitude, location.coords.longitude);

            Alert.alert('Sucesso', 'Localização atualizada com sucesso!');
        } catch (error) {
            console.error('[EditPublicProfileScreen] Location error:', error);
            setLocationError('Erro ao obter localização');
            Alert.alert('Erro', 'Não foi possível obter sua localização. Tente novamente.');
        } finally {
            setIsLoadingLocation(false);
        }
    };

    // Extrair iniciais do nome para fallback do avatar
    const getInitials = (fullName?: string) => {
        if (!fullName) return '?';
        return fullName
            .split(' ')
            .map((n) => n[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    };

    // Handler para editar foto
    const handleEditPhoto = () => {
        Alert.alert(
            'Em breve',
            'A funcionalidade de upload de foto será implementada em breve.'
        );
    };

    // Formatar valor monetário
    const formatCurrency = (text: string) => {
        const cleaned = text.replace(/[^\d.,]/g, '');
        const normalized = cleaned.replace(',', '.');
        return normalized;
    };

    // Salvar perfil público
    const handleSave = async () => {
        try {
            const rate = parseFloat(hourlyRate);
            if (isNaN(rate) || rate < 0) {
                Alert.alert('Erro', 'Por favor, informe um valor válido para a hora/aula.');
                return;
            }

            await updateProfile.mutateAsync({
                bio: bio || undefined,
                vehicle_type: vehicleType || undefined,
                license_category: licenseCategory,
                hourly_rate: rate,
                is_available: isAvailable,
                latitude: latitude || undefined,
                longitude: longitude || undefined,
            });

            Alert.alert('Sucesso', 'Perfil público atualizado com sucesso!');
            navigation.goBack();
        } catch (error) {
            console.error('[EditPublicProfileScreen] Save error:', error);
            Alert.alert('Erro', 'Não foi possível salvar o perfil. Tente novamente.');
        }
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
                    Editar Perfil Público
                </Text>
                <View className="w-10" />
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerClassName="py-6"
                showsVerticalScrollIndicator={false}
                keyboardShouldPersistTaps="handled"
            >
                {/* Banner Dica */}
                <View className="flex-row items-start bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
                    <Lightbulb size={20} color="#D97706" />
                    <View className="flex-1 ml-3">
                        <Text className="text-sm font-semibold text-amber-800">
                            Complete seu perfil!
                        </Text>
                        <Text className="text-xs text-amber-700 mt-1 leading-5">
                            Instrutores com perfil completo recebem mais solicitações de aula.
                            Preencha sua biografia, defina o valor da sua hora/aula e mantenha sua
                            localização atualizada para aparecer nas buscas dos alunos.
                        </Text>
                    </View>
                </View>

                {/* Seção de Foto */}
                <View className="items-center mb-8">
                    <View className="relative">
                        <View className="w-28 h-28 rounded-full border-4 border-blue-100 overflow-hidden bg-gray-200 items-center justify-center">
                            {user?.avatarUrl ? (
                                <Avatar
                                    source={user.avatarUrl}
                                    size="xl"
                                    className="w-full h-full"
                                />
                            ) : (
                                <Text className="text-3xl font-bold text-gray-500">
                                    {getInitials(user?.full_name)}
                                </Text>
                            )}
                        </View>
                        <TouchableOpacity
                            onPress={handleEditPhoto}
                            className="absolute bottom-0 right-0 bg-blue-600 p-2.5 rounded-full border-3 border-white shadow-lg"
                            accessibilityLabel="Alterar foto de perfil"
                        >
                            <Camera size={16} color="#ffffff" />
                        </TouchableOpacity>
                    </View>
                    <Text className="text-sm text-gray-500 mt-3">
                        Toque para alterar a foto
                    </Text>
                </View>

                {/* Seção Dados do Perfil Público */}
                <View className="mb-6">
                    <Text className="text-base font-semibold text-gray-900 mb-4">
                        Dados do Perfil Público
                    </Text>

                    {/* Bio */}
                    <FormInput
                        label="Biografia"
                        value={bio}
                        onChangeText={setBio}
                        placeholder="Informe sua região de atuação (ex: Plano e Entorno) e conte um pouco sobre sua experiência como instrutor..."
                        multiline
                        numberOfLines={4}
                        maxLength={1000}
                    />

                    {/* Tipo de Veículo */}
                    <FormInput
                        label="Marca e Modelo do Veículo"
                        value={vehicleType}
                        onChangeText={setVehicleType}
                        placeholder="Ex: Fiat Mobi"
                    />

                    {/* Categoria CNH */}
                    <CNHSelector
                        selected={licenseCategory}
                        onSelect={setLicenseCategory}
                    />

                    {/* Valor da Hora/Aula */}
                    <FormInput
                        label="Valor da Hora/Aula"
                        value={hourlyRate}
                        onChangeText={(text) => setHourlyRate(formatCurrency(text))}
                        placeholder="80.00"
                        keyboardType="decimal-pad"
                        leftIcon={<DollarSign size={18} color="#9CA3AF" />}
                    />

                    {/* Disponibilidade */}
                    <View className="flex-row items-center justify-between py-4 px-4 bg-gray-50 border border-gray-200 rounded-xl">
                        <View className="flex-1">
                            <Text className="text-base font-medium text-gray-900">
                                Disponível para aulas
                            </Text>
                            <Text className="text-sm text-gray-500 mt-0.5">
                                Quando ativado, você aparece nas buscas
                            </Text>
                        </View>
                        <Switch
                            value={isAvailable}
                            onValueChange={setIsAvailable}
                            trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
                            thumbColor={isAvailable ? '#2563EB' : '#9CA3AF'}
                        />
                    </View>
                </View>

                {/* Seção de Localização */}
                <View className="mb-6">
                    <Text className="text-base font-semibold text-gray-900 mb-2">
                        Localização
                    </Text>
                    <Text className="text-xs text-gray-400 mb-3">
                        Sua localização é usada para aparecer nas buscas de alunos próximos.
                        Para sua segurança, o endereço por extenso não é compartilhado com os alunos, apenas sua distância.
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
                            Salvar Alterações
                        </Text>
                    )}
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
}
