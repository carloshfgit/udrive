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
import { getStudentSchedulings } from '../api/schedulingApi';

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
        queryFn: () => getStudentSchedulings('confirmed', 1, 50),
        enabled,
    });
}
