/**
 * RegisterScreen
 *
 * Tela de cadastro do GoDrive com seleção de tipo de usuário (Aluno/Instrutor).
 */

import React, { useState } from 'react';
import {
    View,
    Text,
    ScrollView,
    StyleSheet,
    KeyboardAvoidingView,
    Platform,
    TouchableOpacity,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Header, BrandLogo, Input } from '../../../shared/components';
import { useAuth } from '../hooks';
import { UserTypeSelector } from '../components';
import type { AuthStackParamList } from '../navigation';

type RegisterScreenNavigationProp = NativeStackNavigationProp<AuthStackParamList, 'Register'>;

export function RegisterScreen() {
    const navigation = useNavigation<RegisterScreenNavigationProp>();
    const { register, login, isRegistering, registerError, loginError } = useAuth();

    const [userType, setUserType] = useState<'student' | 'instructor'>('student');
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [errors, setErrors] = useState<{
        name?: string;
        email?: string;
        password?: string;
        confirmPassword?: string;
    }>({});

    const validateForm = (): boolean => {
        const newErrors: typeof errors = {};

        if (!name.trim()) {
            newErrors.name = 'Nome é obrigatório';
        } else if (name.trim().length < 3) {
            newErrors.name = 'Nome deve ter pelo menos 3 caracteres';
        }

        if (!email.trim()) {
            newErrors.email = 'E-mail é obrigatório';
        } /* else if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = 'E-mail inválido';
        } */

        if (!password.trim()) {
            newErrors.password = 'Senha é obrigatória';
        } else if (password.length < 8) {
            newErrors.password = 'Senha deve ter pelo menos 8 caracteres';
        }

        if (!confirmPassword.trim()) {
            newErrors.confirmPassword = 'Confirme sua senha';
        } else if (password !== confirmPassword) {
            newErrors.confirmPassword = 'As senhas não coincidem';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleRegister = async () => {
        if (!validateForm()) return;

        try {
            // 1. Registrar usuário
            await register({
                full_name: name.trim(),
                email: email.trim(),
                password,
                user_type: userType,
            });

            // 2. Fazer login automático para obter tokens
            await login({
                email: email.trim(),
                password,
            });

            // Navegação será tratada pelo App.tsx ao detectar mudança de autenticação
        } catch (error) {
            console.error('Registration/Login error:', error);
            // Erro já está sendo tratado pelos hooks, mas podemos adicionar feedback visual aqui se necessário
        }
    };

    const handleBack = () => {
        navigation.goBack();
    };

    const handleLogin = () => {
        navigation.navigate('Login');
    };

    // Ícones para inputs
    const UserIcon = () => <Text style={styles.inputIcon}>👤</Text>;
    const EmailIcon = () => <Text style={styles.inputIcon}>✉️</Text>;
    const LockIcon = () => <Text style={styles.inputIcon}>🔒</Text>;

    const VisibilityIcon = ({ visible, onToggle }: { visible: boolean; onToggle: () => void }) => (
        <TouchableOpacity onPress={onToggle}>
            <Text style={styles.inputIcon}>{visible ? '👁️' : '👁️‍🗨️'}</Text>
        </TouchableOpacity>
    );

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <ScrollView
                style={styles.scrollView}
                contentContainerStyle={styles.scrollContent}
                keyboardShouldPersistTaps="handled"
            >
                {/* Header */}
                <Header title="Criar conta" onBack={handleBack} showBack={true} />

                {/* Brand Logo */}
                <BrandLogo title="GoDrive" iconSize="md" />

                {/* Headline */}
                <View style={styles.headlineContainer}>
                    <Text style={styles.headline}>Crie sua conta</Text>
                    <Text style={styles.subheadline}>
                        Comece sua jornada para a habilitação
                    </Text>
                </View>

                {/* User Type Selector */}
                <View style={styles.selectorContainer}>
                    <Text style={styles.selectorLabel}>Eu sou:</Text>
                    <UserTypeSelector
                        value={userType}
                        onChange={setUserType}
                    />
                </View>

                {/* Form */}
                <View style={styles.form}>
                    {/* Name Input */}
                    <Input
                        label="Nome completo"
                        placeholder="Seu nome"
                        autoCapitalize="words"
                        autoComplete="name"
                        value={name}
                        onChangeText={setName}
                        leftIcon={<UserIcon />}
                        error={errors.name}
                    />

                    {/* Email Input */}
                    <Input
                        label="E-mail"
                        placeholder="exemplo@email.com"
                        keyboardType="email-address"
                        autoCapitalize="none"
                        autoComplete="email"
                        value={email}
                        onChangeText={setEmail}
                        leftIcon={<EmailIcon />}
                        error={errors.email}
                        containerStyle={styles.inputMargin}
                    />

                    {/* Password Input */}
                    <Input
                        label="Senha"
                        placeholder="Mínimo 8 caracteres"
                        secureTextEntry={!showPassword}
                        autoComplete="new-password"
                        value={password}
                        onChangeText={setPassword}
                        leftIcon={<LockIcon />}
                        rightIcon={
                            <VisibilityIcon
                                visible={showPassword}
                                onToggle={() => setShowPassword(!showPassword)}
                            />
                        }
                        error={errors.password}
                        containerStyle={styles.inputMargin}
                    />

                    {/* Confirm Password Input */}
                    <Input
                        label="Confirmar senha"
                        placeholder="Repita sua senha"
                        secureTextEntry={!showConfirmPassword}
                        autoComplete="new-password"
                        value={confirmPassword}
                        onChangeText={setConfirmPassword}
                        leftIcon={<LockIcon />}
                        rightIcon={
                            <VisibilityIcon
                                visible={showConfirmPassword}
                                onToggle={() => setShowConfirmPassword(!showConfirmPassword)}
                            />
                        }
                        error={errors.confirmPassword}
                        containerStyle={styles.inputMargin}
                    />

                    {/* Register Error */}
                    {registerError && (
                        <Text style={styles.errorText}>
                            {registerError.message || 'Erro ao criar conta. Tente novamente.'}
                        </Text>
                    )}
                    {loginError && (
                        <Text style={styles.errorText}>
                            {loginError.message || 'Erro ao fazer login.'}
                        </Text>
                    )}
                </View>

                {/* Register Button */}
                <View style={styles.buttonContainer}>
                    <TouchableOpacity
                        style={[styles.registerButton, isRegistering && styles.registerButtonDisabled]}
                        onPress={handleRegister}
                        disabled={isRegistering}
                        activeOpacity={0.8}
                    >
                        <Text style={styles.registerButtonText}>
                            {isRegistering ? 'Criando conta...' : 'Criar conta'}
                        </Text>
                    </TouchableOpacity>
                </View>

                {/* Login Link */}
                <View style={styles.footer}>
                    <Text style={styles.footerText}>
                        Já tem uma conta?{' '}
                        <Text style={styles.footerLink} onPress={handleLogin}>
                            Entrar
                        </Text>
                    </Text>
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#ffffff',
    },
    scrollView: {
        flex: 1,
    },
    scrollContent: {
        flexGrow: 1,
    },
    headlineContainer: {
        paddingHorizontal: 16,
    },
    headline: {
        fontSize: 32,
        fontWeight: '700',
        color: '#111318',
        marginBottom: 4,
    },
    subheadline: {
        fontSize: 16,
        color: '#616f89',
    },
    selectorContainer: {
        paddingHorizontal: 16,
        paddingTop: 24,
    },
    selectorLabel: {
        fontSize: 14,
        fontWeight: '600',
        color: '#111318',
        marginBottom: 12,
    },
    form: {
        paddingHorizontal: 16,
        paddingVertical: 16,
    },
    inputMargin: {
        marginTop: 16,
    },
    inputIcon: {
        fontSize: 20,
        opacity: 0.6,
    },
    errorText: {
        fontSize: 14,
        color: '#ef4444',
        textAlign: 'center',
        marginTop: 16,
    },
    buttonContainer: {
        paddingHorizontal: 16,
        paddingVertical: 8,
    },
    registerButton: {
        backgroundColor: '#135bec',
        paddingVertical: 16,
        borderRadius: 12,
        alignItems: 'center',
        justifyContent: 'center',
        shadowColor: '#135bec',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.25,
        shadowRadius: 8,
        elevation: 4,
    },
    registerButtonDisabled: {
        opacity: 0.7,
    },
    registerButtonText: {
        fontSize: 16,
        fontWeight: '700',
        color: '#ffffff',
    },
    footer: {
        paddingVertical: 40,
        alignItems: 'center',
    },
    footerText: {
        fontSize: 14,
        color: '#6b7280',
    },
    footerLink: {
        color: '#135bec',
        fontWeight: '700',
    },
});
