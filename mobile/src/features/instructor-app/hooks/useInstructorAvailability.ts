/**
 * useInstructorAvailability Hook
 *
 * TanStack Query hooks para gerenciamento de disponibilidade do instrutor.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getAvailabilities,
    createAvailability,
    deleteAvailability,
    CreateAvailabilityRequest,
} from '../api/scheduleApi';

// Query keys
export const INSTRUCTOR_AVAILABILITY_QUERY_KEY = ['instructor', 'availability'];

/**
 * Hook para buscar todas as disponibilidades do instrutor.
 */
export function useAvailabilities() {
    return useQuery({
        queryKey: INSTRUCTOR_AVAILABILITY_QUERY_KEY,
        queryFn: getAvailabilities,
        staleTime: 5 * 60 * 1000, // 5 minutos
    });
}

/**
 * Hook para criar um novo slot de disponibilidade.
 */
export function useCreateAvailability() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: CreateAvailabilityRequest) => createAvailability(data),
        onSuccess: () => {
            // Invalidar cache das disponibilidades para recarregar
            queryClient.invalidateQueries({ queryKey: INSTRUCTOR_AVAILABILITY_QUERY_KEY });
        },
    });
}

/**
 * Hook para remover um slot de disponibilidade.
 */
export function useDeleteAvailability() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (availabilityId: string) => deleteAvailability(availabilityId),
        onSuccess: () => {
            // Invalidar cache das disponibilidades para recarregar
            queryClient.invalidateQueries({ queryKey: INSTRUCTOR_AVAILABILITY_QUERY_KEY });
        },
    });
}
