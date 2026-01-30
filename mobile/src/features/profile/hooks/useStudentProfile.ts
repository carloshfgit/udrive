/**
 * useStudentProfile Hook
 *
 * TanStack Query hooks para gerenciamento de perfil do aluno.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getStudentProfile,
    updateStudentProfile,
    updateLocation,
    UpdateStudentProfileRequest,
    LocationData,
} from '../api/profileApi';
import { useLocationStore } from '../../../lib/store';

// Query keys
export const PROFILE_QUERY_KEY = ['student', 'profile'];

/**
 * Hook para buscar o perfil do aluno.
 */
export function useStudentProfile() {
    return useQuery({
        queryKey: PROFILE_QUERY_KEY,
        queryFn: getStudentProfile,
        staleTime: 5 * 60 * 1000, // 5 minutos
    });
}

/**
 * Hook para atualizar o perfil do aluno.
 */
export function useUpdateStudentProfile() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: UpdateStudentProfileRequest) => updateStudentProfile(data),
        onSuccess: () => {
            // Invalidar cache do perfil para recarregar
            queryClient.invalidateQueries({ queryKey: PROFILE_QUERY_KEY });
        },
    });
}

/**
 * Hook para atualizar a localização do aluno.
 * Atualiza tanto o store local quanto envia ao backend.
 */
export function useUpdateLocation() {
    const setLocation = useLocationStore((state) => state.setLocation);

    return useMutation({
        mutationFn: async (location: LocationData) => {
            // Atualizar store local primeiro
            setLocation(location.latitude, location.longitude);
            // Enviar ao backend
            await updateLocation(location);
        },
    });
}
