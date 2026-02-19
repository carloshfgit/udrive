/**
 * GoDrive Mobile - Payment Hooks
 *
 * TanStack Query hooks para operações de pagamento do aluno.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    createCheckout,
    CreateCheckoutRequest,
    CheckoutResponse,
} from '../api/paymentApi';
import { getStudentSchedulings, cancelBooking, clearStudentCart } from '../api/schedulingApi';

// ============= Query Keys =============

export const CART_ITEMS_QUERY_KEY = ['student', 'cart-items'];

// ============= Hooks =============

/**
 * Hook de mutation para criar um checkout de pagamento.
 *
 * Após sucesso, invalida a query do carrinho para refletir o novo status.
 */
export function useCreateCheckout() {
    const queryClient = useQueryClient();

    return useMutation<CheckoutResponse, Error, CreateCheckoutRequest>({
        mutationFn: createCheckout,
        onSuccess: () => {
            // Invalidar carrinho e lista de agendamentos após criar checkout
            queryClient.invalidateQueries({ queryKey: CART_ITEMS_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
        },
    });
}

/**
 * Hook para remover um item do carrinho.
 *
 * Cancela o agendamento associado (o slot do instrutor é liberado
 * automaticamente) e invalida os caches de carrinho e agendamentos.
 */
export function useRemoveCartItem() {
    const queryClient = useQueryClient();

    return useMutation<void, Error, string>({
        mutationFn: (schedulingId: string) =>
            cancelBooking(schedulingId, 'Removido do carrinho pelo aluno'),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: CART_ITEMS_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
        },
    });
}

/**
 * Hook para limpar o carrinho do aluno.
 * 
 * Cancela todos os agendamentos pendentes no carrinho e invalida o cache.
 */
export function useClearStudentCart() {
    const queryClient = useQueryClient();

    return useMutation<void, Error, void>({
        mutationFn: clearStudentCart,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: CART_ITEMS_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
        },
    });
}

/**
 * Hook para listar itens do carrinho (agendamentos com pagamento pendente).
 *
 * Busca agendamentos com status "confirmed" que ainda não tiveram
 * pagamento concluído. Depende do campo `payment_status` no backend
 * (Etapa 1 do plano).
 *
 * @param enabled - Controla se a query deve ser executada
 */
export function useCartItems(enabled: boolean = true) {
    return useQuery({
        queryKey: CART_ITEMS_QUERY_KEY,
        queryFn: () => getStudentSchedulings(undefined, 1, 50, 'pending'),
        enabled,
    });
}
