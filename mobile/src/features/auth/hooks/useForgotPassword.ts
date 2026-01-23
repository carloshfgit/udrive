/**
 * useForgotPassword Hook
 *
 * Hook para gerenciamento de recuperação de senha.
 */

import { useMutation } from '@tanstack/react-query';
import { api } from '@lib/index';

interface ForgotPasswordData {
    email: string;
}

interface ForgotPasswordResponse {
    message: string;
}

/**
 * Hook para solicitar recuperação de senha.
 */
export function useForgotPassword() {
    const mutation = useMutation({
        mutationFn: async (data: ForgotPasswordData) => {
            const response = await api.post<ForgotPasswordResponse>(
                '/auth/forgot-password',
                data
            );
            return response.data;
        },
    });

    return {
        /** Função para enviar email de recuperação */
        sendResetEmail: mutation.mutateAsync,
        /** Se está processando a requisição */
        isPending: mutation.isPending,
        /** Se a requisição foi bem-sucedida */
        isSuccess: mutation.isSuccess,
        /** Erro da requisição, se houver */
        error: mutation.error,
        /** Resetar estado do hook */
        reset: mutation.reset,
    };
}
