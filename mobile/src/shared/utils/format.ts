/**
 * GoDrive Mobile - Formatting Utilities
 *
 * Utilitários para formatação de dados (moeda, datas, etc).
 */

/**
 * Formata um valor numérico para o padrão de moeda brasileiro (R$).
 * Lida com strings e números para evitar erros de 'toFixed is not a function'.
 *
 * @param value - O valor a ser formatado (number, string ou nulo)
 * @returns String formatada no padrão R$ 0,00
 */
export function formatPrice(value: number | string | undefined | null): string {
    if (value === undefined || value === null) return 'R$ 0,00';

    const numericValue = typeof value === 'string' ? parseFloat(value) : value;

    if (isNaN(numericValue)) return 'R$ 0,00';

    return `R$ ${numericValue.toFixed(2).replace('.', ',')}`;
}
