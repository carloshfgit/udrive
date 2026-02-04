/**
 * GoDrive Mobile - useInstructorAvailability Hook
 *
 * Hook para buscar a disponibilidade semanal de um instrutor.
 */

import { useQuery } from '@tanstack/react-query';
import { getInstructorAvailability, AvailabilityListResponse } from '../api/schedulingApi';

/**
 * Hook para buscar e cachear a disponibilidade semanal de um instrutor.
 *
 * @param instructorId - ID do instrutor
 * @returns Query result com slots de disponibilidade
 */
export function useInstructorAvailability(instructorId: string) {
    return useQuery<AvailabilityListResponse, Error>({
        queryKey: ['instructor', 'availability', instructorId],
        queryFn: () => getInstructorAvailability(instructorId),
        enabled: !!instructorId,
        staleTime: 5 * 60 * 1000, // 5 minutos
    });
}
