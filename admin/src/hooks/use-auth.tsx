'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authService } from '@/services/auth.service';
import { User } from '@/types/user';

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (credentials: any) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const queryClient = useQueryClient();
    const router = useRouter();
    const pathname = usePathname();

    const { data: user, isLoading, isError } = useQuery({
        queryKey: ['me'],
        queryFn: authService.getProfile,
        retry: false,
        enabled: !!(typeof window !== 'undefined' && localStorage.getItem('admin_access_token')),
    });

    const loginMutation = useMutation({
        mutationFn: authService.login,
        onSuccess: (data) => {
            localStorage.setItem('admin_access_token', data.access_token);
            localStorage.setItem('admin_refresh_token', data.refresh_token);

            // Define cookie para o middleware (expira em 1 dia por segurança)
            document.cookie = `admin_access_token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`;

            queryClient.setQueryData(['me'], data.user);
            router.push('/');
        },
    });

    const logout = () => {
        localStorage.removeItem('admin_access_token');
        localStorage.removeItem('admin_refresh_token');

        // Remove cookie
        document.cookie = "admin_access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax";

        queryClient.setQueryData(['me'], null);
        router.push('/login');
    };

    const login = async (credentials: any) => {
        await loginMutation.mutateAsync(credentials);
    };

    return (
        <AuthContext.Provider
            value={{
                user: user ?? null,
                isAuthenticated: !!user,
                isLoading,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
