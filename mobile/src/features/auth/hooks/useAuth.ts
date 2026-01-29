/**
 * useAuth Hook
 *
 * Hook para gerenciamento de autenticação.
 * Encapsula lógica de login, logout e verificação de estado.
 */

import { useCallback } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useAuthStore, tokenManager, queryKeys } from '@lib/index';
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
            const response = await authApi.login(credentials);
            return response.data;
        },
        onSuccess: async (data) => {
            await tokenManager.setTokens(data.access_token, data.refresh_token);
            setUser(data.user);
        },
    });

    // Mutation para registro
    const registerMutation = useMutation({
        mutationFn: async (data: RegisterRequest) => {
            const response = await authApi.register(data);
            return response.data;
        },
        onSuccess: async (data) => {
            await tokenManager.setTokens(data.access_token, data.refresh_token);
            setUser(data.user);
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
