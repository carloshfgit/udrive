/**
 * useInstructorHome Hook
 * 
 * Hook para gerenciar os dados da tela inicial do instrutor.
 */

import { useQuery } from '@tanstack/react-query';
import { getNextClass, getDailySummary } from '../api/homeApi';

export const INSTRUCTOR_HOME_QUERY_KEY = ['instructor', 'home'];

/**
 * Hook principal para os dados da Home do Instrutor.
 */
export function useInstructorHome() {
    // Busca a próxima aula
    const nextClassQuery = useQuery({
        queryKey: [...INSTRUCTOR_HOME_QUERY_KEY, 'next-class'],
        queryFn: getNextClass,
        staleTime: 60 * 1000, // 1 minuto
    });

    // Busca o resumo do dia (ganhos)
    const dailySummaryQuery = useQuery({
        queryKey: [...INSTRUCTOR_HOME_QUERY_KEY, 'daily-summary'],
        queryFn: getDailySummary,
        staleTime: 60 * 1000, // 1 minuto
    });

    return {
        nextClass: nextClassQuery.data,
        dailySummary: dailySummaryQuery.data,
        isLoading: nextClassQuery.isLoading || dailySummaryQuery.isLoading,
        isError: nextClassQuery.isError || dailySummaryQuery.isError,
        refetch: async () => {
            await Promise.all([
                nextClassQuery.refetch(),
                dailySummaryQuery.refetch(),
            ]);
        }
    };
}
