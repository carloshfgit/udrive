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
