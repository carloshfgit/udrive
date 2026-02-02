/**
 * useInstructorProfile Hook
 *
 * TanStack Query hooks para gerenciamento de perfil do instrutor.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getInstructorProfile,
    updateInstructorProfile,
    UpdateInstructorProfileRequest,
} from '../api/instructorApi';

// Query keys
export const INSTRUCTOR_PROFILE_QUERY_KEY = ['instructor', 'profile'];

/**
 * Hook para buscar o perfil do instrutor.
 */
export function useInstructorProfile() {
    return useQuery({
        queryKey: INSTRUCTOR_PROFILE_QUERY_KEY,
        queryFn: getInstructorProfile,
        staleTime: 5 * 60 * 1000, // 5 minutos
    });
}

/**
 * Hook para atualizar o perfil do instrutor.
 */
export function useUpdateInstructorProfile() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: UpdateInstructorProfileRequest) => updateInstructorProfile(data),
        onSuccess: () => {
            // Invalidar cache do perfil para recarregar
            queryClient.invalidateQueries({ queryKey: INSTRUCTOR_PROFILE_QUERY_KEY });
        },
    });
}
