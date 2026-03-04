/**
 * GoDrive Mobile - Filtro de Mensagens Proibidas
 *
 * Detecta tentativas de compartilhar formas de pagamento
 * ou contato externo à plataforma.
 */

interface FilterResult {
    isProhibited: boolean;
    reason: string;
}

// Palavras-chave de pagamento externo
const PAYMENT_KEYWORDS = [
    'pix',
    'chave pix',
    'transferência',
    'transferencia',
    'depósito',
    'deposito',
    'conta bancária',
    'conta bancaria',
    'pagamento por fora',
    'pagar por fora',
    'paga por fora',
    'dinheiro',
    'em espécie',
    'em especie',
    'pagar em mãos',
    'pagar em maos',
    'boleto',
    'ted',
    'doc',
    'nubank',
    'picpay',
    'paypal',
];

// Palavras-chave de contato externo
const CONTACT_KEYWORDS = [
    'whatsapp',
    'whats',
    'zap',
    'zapzap',
    'instagram',
    'insta',
    'ig',
    '@',
    'telegram',
    'facebook',
    'messenger',
    'signal',
    'tiktok',
    'ttk',
    'twitter',
    'tt',
    'me liga',
    'me chama',
    'meu número',
    'meu numero',
    'meu contato',
    'ctt',
    'meu telefone',
    'meu celular',
    'cel',
    'meu email',
    'meu e-mail',
];

// Regex para detectar números de telefone brasileiros
// Ex: (11)99999-8888, 11999998888, +55 11 99999-8888
const PHONE_REGEX =
    /(?:\+?55\s?)?(?:\(?\d{2}\)?[\s.-]?)?\d{4,5}[\s.-]?\d{4}/;

// Regex para detectar e-mails
const EMAIL_REGEX =
    /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/;

// Regex para detectar URLs
const URL_REGEX =
    /(?:https?:\/\/|www\.)[^\s]+/i;

/**
 * Verifica se o texto contém conteúdo proibido.
 */
export function checkProhibitedContent(text: string): FilterResult {
    const normalizedText = text.toLowerCase().trim();

    // Verificar palavras-chave de pagamento
    for (const keyword of PAYMENT_KEYWORDS) {
        if (normalizedText.includes(keyword)) {
            return {
                isProhibited: true,
                reason:
                    'Não é permitido compartilhar informações de pagamento por fora da plataforma. Todos os pagamentos devem ser feitos pelo app.',
            };
        }
    }

    // Verificar palavras-chave de contato externo
    for (const keyword of CONTACT_KEYWORDS) {
        if (normalizedText.includes(keyword)) {
            return {
                isProhibited: true,
                reason:
                    'Não é permitido compartilhar formas de contato fora da plataforma. Use o chat do app para se comunicar.',
            };
        }
    }

    // Verificar padrões de telefone
    if (PHONE_REGEX.test(normalizedText)) {
        return {
            isProhibited: true,
            reason:
                'Não é permitido compartilhar números de telefone. Use o chat do app para se comunicar.',
        };
    }

    // Verificar e-mails
    if (EMAIL_REGEX.test(normalizedText)) {
        return {
            isProhibited: true,
            reason:
                'Não é permitido compartilhar endereços de e-mail. Use o chat do app para se comunicar.',
        };
    }

    // Verificar URLs
    if (URL_REGEX.test(normalizedText)) {
        return {
            isProhibited: true,
            reason:
                'Não é permitido compartilhar links externos. Use o chat do app para se comunicar.',
        };
    }

    return { isProhibited: false, reason: '' };
}
