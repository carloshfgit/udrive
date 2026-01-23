/**
 * ForgotPasswordScreen
 *
 * Tela de recuperação de senha do GoDrive.
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
import { useForgotPassword } from '../hooks';
import type { AuthStackParamList } from '../navigation';

type ForgotPasswordScreenNavigationProp = NativeStackNavigationProp<AuthStackParamList, 'ForgotPassword'>;

export function ForgotPasswordScreen() {
    const navigation = useNavigation<ForgotPasswordScreenNavigationProp>();
    const { sendResetEmail, isPending, isSuccess, error } = useForgotPassword();

    const [email, setEmail] = useState('');
    const [emailError, setEmailError] = useState<string | undefined>();

    const validateEmail = (): boolean => {
        if (!email.trim()) {
            setEmailError('E-mail é obrigatório');
            return false;
        }

        if (!/\S+@\S+\.\S+/.test(email)) {
            setEmailError('E-mail inválido');
            return false;
        }

        setEmailError(undefined);
        return true;
    };

    const handleSendEmail = async () => {
        if (!validateEmail()) return;

        try {
            await sendResetEmail({ email: email.trim() });
        } catch {
            // Erro já está em error
        }
    };

    const handleBack = () => {
        navigation.goBack();
    };

    const handleLogin = () => {
        navigation.navigate('Login');
    };

    // Ícone de email
    const EmailIcon = () => <Text style={styles.inputIcon}>✉️</Text>;

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
                <Header title="Recuperar senha" onBack={handleBack} showBack={true} />

                {/* Brand Logo */}
                <BrandLogo title="GoDrive" iconSize="md" />

                {/* Headline */}
                <View style={styles.headlineContainer}>
                    <Text style={styles.headline}>Esqueceu sua senha?</Text>
                    <Text style={styles.subheadline}>
                        Não se preocupe! Digite seu e-mail e enviaremos instruções para redefinir sua senha.
                    </Text>
                </View>

                {/* Success Message */}
                {isSuccess ? (
                    <View style={styles.successContainer}>
                        <View style={styles.successIcon}>
                            <Text style={styles.successIconText}>✅</Text>
                        </View>
                        <Text style={styles.successTitle}>E-mail enviado!</Text>
                        <Text style={styles.successText}>
                            Verifique sua caixa de entrada e siga as instruções para redefinir sua senha.
                        </Text>
                        <TouchableOpacity
                            style={styles.backToLoginButton}
                            onPress={handleLogin}
                            activeOpacity={0.8}
                        >
                            <Text style={styles.backToLoginButtonText}>Voltar para o login</Text>
                        </TouchableOpacity>
                    </View>
                ) : (
                    <>
                        {/* Form */}
                        <View style={styles.form}>
                            <Input
                                label="E-mail"
                                placeholder="exemplo@email.com"
                                keyboardType="email-address"
                                autoCapitalize="none"
                                autoComplete="email"
                                value={email}
                                onChangeText={setEmail}
                                leftIcon={<EmailIcon />}
                                error={emailError}
                            />

                            {/* API Error */}
                            {error && (
                                <Text style={styles.errorText}>
                                    {error.message || 'Erro ao enviar e-mail. Tente novamente.'}
                                </Text>
                            )}
                        </View>

                        {/* Send Button */}
                        <View style={styles.buttonContainer}>
                            <TouchableOpacity
                                style={[styles.sendButton, isPending && styles.sendButtonDisabled]}
                                onPress={handleSendEmail}
                                disabled={isPending}
                                activeOpacity={0.8}
                            >
                                <Text style={styles.sendButtonText}>
                                    {isPending ? 'Enviando...' : 'Enviar instruções'}
                                </Text>
                            </TouchableOpacity>
                        </View>

                        {/* Back to Login */}
                        <View style={styles.footer}>
                            <Text style={styles.footerText}>
                                Lembrou a senha?{' '}
                                <Text style={styles.footerLink} onPress={handleLogin}>
                                    Entrar
                                </Text>
                            </Text>
                        </View>
                    </>
                )}
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
        marginBottom: 8,
    },
    subheadline: {
        fontSize: 16,
        color: '#616f89',
        lineHeight: 24,
    },
    form: {
        paddingHorizontal: 16,
        paddingVertical: 32,
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
    sendButton: {
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
    sendButtonDisabled: {
        opacity: 0.7,
    },
    sendButtonText: {
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
    // Success state styles
    successContainer: {
        paddingHorizontal: 16,
        paddingVertical: 32,
        alignItems: 'center',
    },
    successIcon: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 24,
    },
    successIconText: {
        fontSize: 40,
    },
    successTitle: {
        fontSize: 24,
        fontWeight: '700',
        color: '#111318',
        marginBottom: 8,
    },
    successText: {
        fontSize: 16,
        color: '#616f89',
        textAlign: 'center',
        lineHeight: 24,
        marginBottom: 32,
    },
    backToLoginButton: {
        backgroundColor: '#135bec',
        paddingVertical: 16,
        paddingHorizontal: 32,
        borderRadius: 12,
        shadowColor: '#135bec',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.25,
        shadowRadius: 8,
        elevation: 4,
    },
    backToLoginButtonText: {
        fontSize: 16,
        fontWeight: '700',
        color: '#ffffff',
    },
});
