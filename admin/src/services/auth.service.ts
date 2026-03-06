import api from '@/lib/api';
import { LoginResponse } from '@/types/auth';
import { User } from '@/types/user';

export const authService = {
    async login(credentials: Record<string, any>): Promise<LoginResponse> {
        const { data } = await api.post<LoginResponse>('/auth/login', {
            email: credentials.email,
            password: credentials.password,
        });
        return data;
    },

    async getProfile(): Promise<User> {
        const { data } = await api.get<User>('/auth/me');
        return data;
    },

    async logout(): Promise<void> {
        // Normalmente logout no cliente é apenas limpar o storage
        // mas se houver um endpoint no backend:
        // await api.post('/auth/logout');
    }
};
