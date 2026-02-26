/**
 * LoginScreen
 *
 * Tela de login do GoDrive seguindo o design proposto.
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
import { Header, BrandLogo, Input, Divider } from '../../../shared/components';
import { useAuth } from '../hooks';
import { SocialLoginButtons } from '../components';
import type { AuthStackParamList } from '../navigation';

type LoginScreenNavigationProp = NativeStackNavigationProp<AuthStackParamList, 'Login'>;

export function LoginScreen() {
    const navigation = useNavigation<LoginScreenNavigationProp>();
    const { login, isLoggingIn, loginError } = useAuth();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

    const validateForm = (): boolean => {
        const newErrors: { email?: string; password?: string } = {};

        if (!email.trim()) {
            newErrors.email = 'E-mail é obrigatório';
        } /* else if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = 'E-mail inválido';
        } */

        if (!password.trim()) {
            newErrors.password = 'Senha é obrigatória';
        } else if (password.length < 6) {
            newErrors.password = 'Senha deve ter pelo menos 6 caracteres';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleLogin = async () => {
        if (!validateForm()) return;

        try {
            await login({ email: email.trim(), password });
            // Navegação será tratada pelo App.tsx ao detectar mudança de autenticação
        } catch {
            // Erro já está em loginError
        }
    };

    const handleForgotPassword = () => {
        navigation.navigate('ForgotPassword');
    };

    const handleCreateAccount = () => {
        navigation.navigate('Register');
    };

    const handleBack = () => {
        // Por enquanto, não faz nada na tela de login inicial
    };

    // Ícones para inputs
    const EmailIcon = () => <Text style={styles.inputIcon}>✉️</Text>;
    const LockIcon = () => <Text style={styles.inputIcon}>🔒</Text>;
    const VisibilityIcon = () => (
        <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
            <Text style={styles.inputIcon}>{showPassword ? '👁️' : '👁️‍🗨️'}</Text>
        </TouchableOpacity>
    );

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        >
            <ScrollView
                style={styles.scrollView}
                contentContainerStyle={styles.scrollContent}
                keyboardShouldPersistTaps="handled"
            >
                {/* Header */}
                <Header title="Login" onBack={handleBack} showBack={true} />

                {/* Brand Logo */}
                <BrandLogo title="GoDrive" iconSize="md" />

                {/* Headline */}
                <View style={styles.headlineContainer}>
                    <Text style={styles.headline}>Bem-vindo de volta!</Text>
                    <Text style={styles.subheadline}>
                        Pronto para sua próxima aula de direção?
                    </Text>
                </View>

                {/* Form */}
                <View style={styles.form}>
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
                    />

                    {/* Password Input */}
                    <View style={styles.passwordContainer}>
                        <View style={styles.passwordLabelRow}>
                            <Text style={styles.label}>Senha</Text>
                            <TouchableOpacity onPress={handleForgotPassword}>
                                <Text style={styles.forgotPasswordLink}>Esqueceu a senha?</Text>
                            </TouchableOpacity>
                        </View>
                        <Input
                            placeholder="••••••••"
                            secureTextEntry={!showPassword}
                            autoComplete="password"
                            value={password}
                            onChangeText={setPassword}
                            leftIcon={<LockIcon />}
                            rightIcon={<VisibilityIcon />}
                            error={errors.password}
                        />
                    </View>

                    {/* Login Error */}
                    {loginError && (
                        <Text style={styles.errorText}>
                            {loginError.message || 'Erro ao fazer login. Tente novamente.'}
                        </Text>
                    )}
                </View>

                {/* Login Button */}
                <View style={styles.buttonContainer}>
                    <TouchableOpacity
                        style={[styles.loginButton, isLoggingIn && styles.loginButtonDisabled]}
                        onPress={handleLogin}
                        disabled={isLoggingIn}
                        activeOpacity={0.8}
                    >
                        <Text style={styles.loginButtonText}>
                            {isLoggingIn ? 'Entrando...' : 'Entrar'}
                        </Text>
                    </TouchableOpacity>
                </View>

                {/* Divider */}
                <Divider text="Ou entre com" />

                {/* Social Login */}
                <SocialLoginButtons />

                {/* Create Account */}
                <View style={styles.footer}>
                    <Text style={styles.footerText}>
                        Não tem uma conta?{' '}
                        <Text style={styles.footerLink} onPress={handleCreateAccount}>
                            Criar conta
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
    form: {
        paddingHorizontal: 16,
        paddingVertical: 24,
        gap: 8,
    },
    passwordContainer: {
        marginTop: 8,
    },
    passwordLabelRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    label: {
        fontSize: 14,
        fontWeight: '600',
        color: '#111318',
    },
    forgotPasswordLink: {
        fontSize: 14,
        fontWeight: '500',
        color: '#135bec',
    },
    inputIcon: {
        fontSize: 20,
        opacity: 0.6,
    },
    errorText: {
        fontSize: 14,
        color: '#ef4444',
        textAlign: 'center',
        marginTop: 8,
    },
    buttonContainer: {
        paddingHorizontal: 16,
        paddingVertical: 8,
    },
    loginButton: {
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
    loginButtonDisabled: {
        opacity: 0.7,
    },
    loginButtonText: {
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
