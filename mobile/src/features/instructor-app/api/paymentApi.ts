/**
 * Instructor Payment API
 *
 * Funções para comunicação com endpoints de pagamento/OAuth do instrutor.
 */

import api, { INSTRUCTOR_API } from '../../../lib/axios';

// ============= Types =============

export interface OAuthAuthorizeResponse {
    authorization_url: string;
    state: string;
}

export interface InstructorEarnings {
    instructor_id: string;
    total_earnings: number;
    monthly_earnings: number;
    completed_lessons: number;
    period_start: string | null;
    period_end: string | null;
}

// ============= API Functions =============

/**
 * Obtém a URL de autorização OAuth do Mercado Pago.
 *
 * O instrutor deve abrir essa URL no browser para vincular
 * sua conta Mercado Pago ao GoDrive.
 */
export async function getOAuthAuthorizeUrl(returnUrl?: string): Promise<OAuthAuthorizeResponse> {
    const response = await api.get<OAuthAuthorizeResponse>(
        `${INSTRUCTOR_API}/oauth/mercadopago/authorize`,
        { params: { return_url: returnUrl } }
    );
    return response.data;
}

/**
 * Obtém o resumo financeiro do instrutor autenticado.
 * Retorna os ganhos totais, ganhos do mês corrente e aulas concluídas.
 */
export async function getInstructorEarnings(): Promise<InstructorEarnings> {
    const response = await api.get<InstructorEarnings>(`${INSTRUCTOR_API}/earnings`);
    return response.data;
}
