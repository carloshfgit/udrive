/**
 * GoDrive Mobile - Payment API
 *
 * Funções para comunicação com endpoints de pagamento do aluno.
 */

import api, { STUDENT_API } from '../../../../lib/axios';

// ============= Types =============

export interface CreateCheckoutRequest {
    scheduling_ids: string[];
    student_id: string;
    student_email?: string;
}

export interface CheckoutResponse {
    payment_id: string;
    preference_id: string;
    checkout_url: string;
    sandbox_url: string | null;
    status: string;
}

// ============= API Functions =============

/**
 * Cria um checkout de pagamento via Mercado Pago Checkout Pro.
 *
 * Retorna a URL de checkout para redirecionar o aluno ao MP.
 * O backend cria a preferência de pagamento e retorna o init_point.
 */
export async function createCheckout(
    data: CreateCheckoutRequest
): Promise<CheckoutResponse> {
    const response = await api.post<CheckoutResponse>(
        `${STUDENT_API}/payments/checkout`,
        data
    );
    return response.data;
}
