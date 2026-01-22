/**
 * useAuth Hook
 *
 * Hook para gerenciamento de autenticação.
 * Encapsula lógica de login, logout e verificação de estado.
 */

import { useCallback, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useAuthStore, api, tokenManager, queryKeys } from '@lib/index';

interface LoginCredentials {
    email: string;
    password: string;
}

interface RegisterData {
    email: string;
    password: string;
    name: string;
    type: 'student' | 'instructor';
}

interface AuthResponse {
    access_token: string;
    refresh_token: string;
    user: {
        id: string;
        email: string;
        name: string;
        type: 'student' | 'instructor' | 'admin';
        avatarUrl?: string;
    };
}

/**
 * Hook para gerenciamento de autenticação.
 */
export function useAuth() {
    const { user, isAuthenticated, isLoading, setUser, setLoading, logout: storeLogout } = useAuthStore();

    // Query para buscar usuário atual
    const userQuery = useQuery({
        queryKey: queryKeys.auth.user(),
        queryFn: async () => {
            const response = await api.get<AuthResponse['user']>('/auth/me');
            return response.data;
        },
        enabled: false, // Não executar automaticamente
        retry: false,
    });

    // Mutation para login
    const loginMutation = useMutation({
        mutationFn: async (credentials: LoginCredentials) => {
            const response = await api.post<AuthResponse>('/auth/login', credentials);
            return response.data;
        },
        onSuccess: async (data) => {
            await tokenManager.setTokens(data.access_token, data.refresh_token);
            setUser(data.user);
        },
    });

    // Mutation para registro
    const registerMutation = useMutation({
        mutationFn: async (data: RegisterData) => {
            const response = await api.post<AuthResponse>('/auth/register', data);
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
            await api.post('/auth/logout');
        } catch {
            // Ignorar erro de logout
        } finally {
            await tokenManager.clearTokens();
            storeLogout();
        }
    }, [storeLogout]);

    // Verificar autenticação ao iniciar
    useEffect(() => {
        const checkAuth = async () => {
            setLoading(true);

            const hasToken = await tokenManager.hasValidToken();

            if (hasToken) {
                try {
                    const { data } = await api.get<AuthResponse['user']>('/auth/me');
                    setUser(data);
                } catch {
                    await tokenManager.clearTokens();
                    setUser(null);
                }
            } else {
                setUser(null);
            }
        };

        checkAuth();
    }, [setLoading, setUser]);

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
