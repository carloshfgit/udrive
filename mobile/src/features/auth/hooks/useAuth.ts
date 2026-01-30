/**
 * useAuth Hook
 *
 * Hook para gerenciamento de autenticação.
 * Encapsula lógica de login, logout e verificação de estado.
 */

import { useCallback } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useAuthStore, tokenManager, queryKeys, api } from '@lib/index';
import { authApi, LoginRequest, RegisterRequest, AuthResponse } from '../api/authApi';

/**
 * Hook para gerenciamento de autenticação.
 */
export function useAuth() {
    const { user, isAuthenticated, isLoading, setUser, logout: storeLogout } = useAuthStore();

    // Query para buscar usuário atual
    const userQuery = useQuery({
        queryKey: queryKeys.auth.user(),
        queryFn: async () => {
            const response = await authApi.me();
            return response.data;
        },
        enabled: false, // Não executar automaticamente
        retry: false,
    });

    // Mutation para login
    const loginMutation = useMutation({
        mutationFn: async (credentials: LoginRequest) => {
            // 1. Login para obter tokens
            const loginResponse = await authApi.login(credentials);
            console.log('Login Response Data:', JSON.stringify(loginResponse.data, null, 2));
            const { access_token, refresh_token } = loginResponse.data;

            if (!access_token || !refresh_token) {
                console.error('Login response invalid:', loginResponse.data);
                throw new Error(`Falha no login: Tokens não recebidos. Recebido: ${JSON.stringify(loginResponse.data)}`);
            }

            // 2. Salvar tokens
            await tokenManager.setTokens(access_token, refresh_token);

            // 3. Configurar header manualmente para a próxima requisição
            // (necessário porque o axios interceptor pode não pegar o token do SecureStore imediatamente)
            api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

            // 4. Buscar dados do usuário
            const userResponse = await authApi.me();

            return {
                tokens: loginResponse.data,
                user: userResponse.data
            };
        },
        onSuccess: async (data) => {
            // Estado global já pode ser atualizado
            setUser(data.user);
        },
    });

    // Mutation para registro
    const registerMutation = useMutation({
        mutationFn: async (data: RegisterRequest) => {
            const response = await authApi.register(data);
            return response.data;
        },
    });

    // Função de logout
    const logout = useCallback(async () => {
        try {
            await authApi.logout();
        } catch {
            // Ignorar erro de logout
        } finally {
            await tokenManager.clearTokens();
            storeLogout();
        }
    }, [storeLogout]);

    return {
        // Estado
        user,
        isAuthenticated,
        isLoading,

        // Ações
        login: loginMutation.mutateAsync,
        register: registerMutation.mutateAsync,
        logout,
        refetchUser: userQuery.refetch,

        // Estados das mutations
        isLoggingIn: loginMutation.isPending,
        isRegistering: registerMutation.isPending,
        loginError: loginMutation.error,
        registerError: registerMutation.error,
    };
}
