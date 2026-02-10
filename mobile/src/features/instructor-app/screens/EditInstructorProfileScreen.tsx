/**
 * EditInstructorProfileScreen
 *
 * Tela de edição de dados pessoais do instrutor.
 * Contém apenas informações privadas: nome, CPF, telefone, data de nascimento e sexo.
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
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { ChevronLeft, ShieldCheck } from 'lucide-react-native';

import { useAuthStore } from '../../../lib/store';
import { useInstructorProfile, useUpdateInstructorProfile } from '../hooks/useInstructorProfile';

// Componente de input customizado para esta tela
interface FormInputProps {
    label: string;
    value: string;
    onChangeText: (text: string) => void;
    placeholder?: string;
    keyboardType?: 'default' | 'numeric' | 'decimal-pad' | 'phone-pad';
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
            <View className={`flex-row items-start bg-gray-50 border border-gray-200 rounded-xl overflow-hidden ${!editable ? 'opacity-60' : ''}`}>
                <TextInput
                    value={value}
                    onChangeText={onChangeText}
                    placeholder={placeholder}
                    keyboardType={keyboardType}
                    editable={editable}
                    textAlignVertical="center"
                    className="flex-1 text-base text-gray-900 px-4 py-3.5"
                    placeholderTextColor="#9CA3AF"
                />
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

    // API hooks
    const { data: profile, isLoading: isLoadingProfile } = useInstructorProfile();
    const updateProfile = useUpdateInstructorProfile();

    // Dados pessoais
    const [name, setName] = useState(user?.full_name || '');
    const [phone, setPhone] = useState('');
    const [cpf, setCpf] = useState('');
    const [birthDate, setBirthDate] = useState('');
    const [biologicalSex, setBiologicalSex] = useState<'male' | 'female' | null>(null);

    // Carregar dados do perfil quando disponível
    useEffect(() => {
        if (profile) {
            if (profile.full_name) setName(profile.full_name);
            if (profile.phone) setPhone(profile.phone);
            if (profile.cpf) setCpf(profile.cpf);

            // Formatando data de YYYY-MM-DD para DD/MM/YYYY
            if (profile.birth_date) {
                const [year, month, day] = profile.birth_date.split('-');
                setBirthDate(`${day}/${month}/${year}`);
            }

            if (profile.biological_sex) {
                setBiologicalSex(profile.biological_sex as 'male' | 'female');
            }
        }
    }, [profile]);

    // Carregar nome do user
    useEffect(() => {
        if (user?.full_name) {
            setName(user.full_name);
        }
    }, [user]);

    // Converter data BR (DD/MM/YYYY) para ISO (YYYY-MM-DD)
    const convertDateToISO = (brDate: string): string | null => {
        if (!brDate || brDate.length < 10) return null;
        const parts = brDate.split('/');
        if (parts.length !== 3) return null;
        const [day, month, year] = parts;
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
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

    // Salvar dados pessoais
    const handleSave = async () => {
        try {
            const isoBirthDate = convertDateToISO(birthDate);

            await updateProfile.mutateAsync({
                full_name: name,
                phone: phone || undefined,
                cpf: cpf || undefined,
                birth_date: isoBirthDate,
                biological_sex: biologicalSex || undefined,
            });

            Alert.alert('Sucesso', 'Informações pessoais atualizadas com sucesso!');
            navigation.goBack();
        } catch (error) {
            console.error('[EditInstructorProfileScreen] Save error:', error);
            Alert.alert('Erro', 'Não foi possível salvar as informações. Tente novamente.');
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
                        label="Telefone para contato"
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
