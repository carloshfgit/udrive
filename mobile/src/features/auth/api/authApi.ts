/**
 * Auth API
 *
 * Funções tipadas para chamadas à API de autenticação.
 */

import { api } from '@lib/axios';

// Tipos de requisição
export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    password: string;
    full_name: string;
    user_type: 'student' | 'instructor';
}

export interface ForgotPasswordRequest {
    email: string;
}

export interface ResetPasswordRequest {
    token: string;
    password: string;
}

// Tipos de resposta
export interface User {
    id: string;
    email: string;
    full_name: string;
    type: 'student' | 'instructor' | 'admin';
    avatarUrl?: string;
}

export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface MessageResponse {
    message: string;
}

/**
 * Funções de API para autenticação.
 */
export const authApi = {
    /**
     * Login com email e senha.
     */
    login: (data: LoginRequest) =>
        api.post<AuthResponse>('/auth/login', data),

    /**
     * Registro de novo usuário.
     */
    register: (data: RegisterRequest) =>
        api.post<User>('/auth/register', data),

    /**
     * Solicitar recuperação de senha.
     */
    forgotPassword: (email: string) =>
        api.post<MessageResponse>('/auth/forgot-password', { email }),

    /**
     * Redefinir senha com token.
     */
    resetPassword: (data: ResetPasswordRequest) =>
        api.post<MessageResponse>('/auth/reset-password', data),

    /**
     * Obter dados do usuário autenticado.
     */
    me: () =>
        api.get<User>('/auth/me'),

    /**
     * Logout do usuário.
     */
    logout: () =>
        api.post('/auth/logout'),
};
