/**
 * EditInstructorProfileScreen
 *
 * Tela de edição do perfil do instrutor.
 * Inclui dados pessoais (nome, CPF, telefone, data, localização) e profissionais.
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
} from 'lucide-react-native';
import * as Location from 'expo-location';

import { useAuthStore, useLocationStore } from '../../../lib/store';
import { useInstructorProfile, useUpdateInstructorProfile } from '../hooks/useInstructorProfile';
import { Avatar } from '../../../shared/components';

// Categorias de CNH disponíveis
const CNH_CATEGORIES = ['A', 'B', 'AB', 'C', 'D', 'E'];

// Componente de input customizado para esta tela
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

// Componente de seleção de sexo biológico
interface BiologicalSexSelectorProps {
    selected: 'male' | 'female' | null;
    onSelect: (sex: 'male' | 'female') => void;
}

function BiologicalSexSelector({ selected, onSelect }: BiologicalSexSelectorProps) {
    return (
        <View className="mb-4">
            <Text className="text-sm font-medium text-gray-600 mb-2">
                Sexo Biológico
            </Text>
            <View className="flex-row gap-3">
                <TouchableOpacity
                    onPress={() => onSelect('female')}
                    className={`
                        flex-1 py-3.5 rounded-xl border-2 items-center
                        ${selected === 'female'
                            ? 'bg-pink-500 border-pink-500'
                            : 'bg-white border-gray-200'
                        }
                    `}
                >
                    <Text
                        className={`
                            text-base font-semibold
                            ${selected === 'female' ? 'text-white' : 'text-gray-700'}
                        `}
                    >
                        Feminino
                    </Text>
                </TouchableOpacity>
                <TouchableOpacity
                    onPress={() => onSelect('male')}
                    className={`
                        flex-1 py-3.5 rounded-xl border-2 items-center
                        ${selected === 'male'
                            ? 'bg-blue-600 border-blue-600'
                            : 'bg-white border-gray-200'
                        }
                    `}
                >
                    <Text
                        className={`
                            text-base font-semibold
                            ${selected === 'male' ? 'text-white' : 'text-gray-700'}
                        `}
                    >
                        Masculino
                    </Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}

export function EditInstructorProfileScreen() {
    const navigation = useNavigation();
    const { user } = useAuthStore();
    const { latitude, longitude, setLocation } = useLocationStore();

    // API hooks
    const { data: profile, isLoading: isLoadingProfile } = useInstructorProfile();
    const updateProfile = useUpdateInstructorProfile();

    // Personal info state
    const [name, setName] = useState(user?.full_name || '');
    const [phone, setPhone] = useState('');
    const [cpf, setCpf] = useState('');
    const [birthDate, setBirthDate] = useState('');

    // Professional info state
    const [bio, setBio] = useState('');
    const [vehicleType, setVehicleType] = useState('');
    const [licenseCategory, setLicenseCategory] = useState('B');
    const [hourlyRate, setHourlyRate] = useState('');
    const [isAvailable, setIsAvailable] = useState(true);
    const [biologicalSex, setBiologicalSex] = useState<'male' | 'female' | null>(null);

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

            // Carregar dados pessoais do perfil (mais atualizado que user store)
            if (profile.full_name) setName(profile.full_name);
            if (profile.phone) setPhone(profile.phone);
            if (profile.cpf) setCpf(profile.cpf);

            // Formatando data de YYYY-MM-DD para DD/MM/YYYY
            if (profile.birth_date) {
                const [year, month, day] = profile.birth_date.split('-');
                setBirthDate(`${day}/${month}/${year}`);
            }

            // Carregar sexo biológico
            if (profile.biological_sex) {
                setBiologicalSex(profile.biological_sex as 'male' | 'female');
            }
        }
    }, [profile]);

    // Converter data BR (DD/MM/YYYY) para ISO (YYYY-MM-DD)
    const convertDateToISO = (brDate: string): string | null => {
        if (!brDate || brDate.length < 10) return null;
        const parts = brDate.split('/');
        if (parts.length !== 3) return null;
        const [day, month, year] = parts;
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    };

    // Carregar nome do user
    useEffect(() => {
        if (user?.full_name) {
            setName(user.full_name);
        }
    }, [user]);

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
            console.log('[EditInstructorProfileScreen] Geocoding error:', error);
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

            // Atualizar store local
            setLocation(location.coords.latitude, location.coords.longitude);

            // Feedback visual
            Alert.alert('Sucesso', 'Localização atualizada com sucesso!');

        } catch (error) {
            console.error('[EditInstructorProfileScreen] Location error:', error);
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

    // Formatar valor monetário
    const formatCurrency = (text: string) => {
        const cleaned = text.replace(/[^\d.,]/g, '');
        const normalized = cleaned.replace(',', '.');
        return normalized;
    };

    // Salvar perfil
    const handleSave = async () => {
        try {
            // Validar valor da hora
            const rate = parseFloat(hourlyRate);
            if (isNaN(rate) || rate < 0) {
                Alert.alert('Erro', 'Por favor, informe um valor válido para a hora/aula.');
                return;
            }

            // Converter data para ISO
            const isoBirthDate = convertDateToISO(birthDate);

            await updateProfile.mutateAsync({
                full_name: name,
                phone: phone || undefined,
                cpf: cpf || undefined,
                birth_date: isoBirthDate,
                bio: bio || undefined,
                vehicle_type: vehicleType || undefined,
                license_category: licenseCategory,
                hourly_rate: rate,
                is_available: isAvailable,
                biological_sex: biologicalSex || undefined,
                latitude: latitude || undefined,
                longitude: longitude || undefined,
            });

            Alert.alert('Sucesso', 'Perfil atualizado com sucesso!');
            navigation.goBack();
        } catch (error) {
            console.error('[EditInstructorProfileScreen] Save error:', error);
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
                    Editar Perfil
                </Text>
                <View className="w-10" />
            </View>

            <ScrollView
                className="flex-1 px-4"
                contentContainerClassName="py-6"
                showsVerticalScrollIndicator={false}
                keyboardShouldPersistTaps="handled"
            >
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
                        {/* Camera Badge */}
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

                {/* Seção Dados Pessoais */}
                <View className="mb-6">
                    <Text className="text-base font-semibold text-gray-900 mb-4">
                        Dados Pessoais
                    </Text>

                    {/* Nome */}
                    <FormInput
                        label="Nome Completo"
                        value={name}
                        onChangeText={setName}
                        placeholder="Seu nome"
                        editable={true}
                    />

                    {/* Telefone */}
                    <FormInput
                        label="Telefone"
                        value={phone}
                        onChangeText={(text) => setPhone(formatPhone(text))}
                        placeholder="(00) 00000-0000"
                        keyboardType="phone-pad"
                    />

                    {/* CPF */}
                    <FormInput
                        label="CPF"
                        value={cpf}
                        onChangeText={(text) => setCpf(formatCPF(text))}
                        placeholder="000.000.000-00"
                        keyboardType="numeric"
                    />

                    {/* Data de Nascimento */}
                    <FormInput
                        label="Data de Nascimento"
                        value={birthDate}
                        onChangeText={(text) => setBirthDate(formatDate(text))}
                        placeholder="DD/MM/AAAA"
                        keyboardType="numeric"
                    />

                    {/* Sexo Biológico */}
                    <BiologicalSexSelector
                        selected={biologicalSex}
                        onSelect={setBiologicalSex}
                    />

                    {/* Seção de Localização */}
                    <View className="mb-4">
                        <Text className="text-sm font-medium text-gray-600 mb-2">
                            Localização
                        </Text>
                        <Text className="text-xs text-gray-400 mb-3">
                            Sua localização é usada para aparecer nas buscas de alunos próximos.
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
                </View>

                {/* Seção Dados Profissionais */}
                <View className="mb-6">
                    <Text className="text-base font-semibold text-gray-900 mb-4">
                        Dados Profissionais
                    </Text>

                    {/* Bio */}
                    <FormInput
                        label="Biografia"
                        value={bio}
                        onChangeText={setBio}
                        placeholder="Conte um pouco sobre sua experiência como instrutor..."
                        multiline
                        numberOfLines={4}
                        maxLength={1000}
                    />

                    {/* Tipo de Veículo */}
                    <FormInput
                        label="Tipo de Veículo"
                        value={vehicleType}
                        onChangeText={setVehicleType}
                        placeholder="Ex: Hatch, Sedan, SUV"
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
