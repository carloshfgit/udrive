/**
 * GoDrive Mobile - useInstructorProfile Hook
 *
 * Hook para buscar detalhes do perfil de um instrutor usando TanStack Query.
 */

import { useQuery } from '@tanstack/react-query';
import { getInstructorById, InstructorDetail } from '../api/instructorApi';

/**
 * Hook para buscar e cachear os detalhes de um instrutor.
 *
 * @param instructorId - ID do instrutor a ser buscado
 * @returns Query result com dados do instrutor
 */
export function useInstructorProfile(instructorId: string) {
    return useQuery<InstructorDetail, Error>({
        queryKey: ['instructor', 'profile', instructorId],
        queryFn: () => getInstructorById(instructorId),
        enabled: !!instructorId,
        staleTime: 5 * 60 * 1000, // 5 minutos
    });
}
