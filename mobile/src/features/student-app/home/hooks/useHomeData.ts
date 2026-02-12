/**
 * GoDrive Mobile - Student Home Hooks
 * 
 * Custom hooks para gerenciar os dados da Home do aluno.
 */

import { useQuery } from '@tanstack/react-query';
import { getHomeProfile, getUpcomingLessons, StudentProfileResponse } from '../api/homeApi';
import { SchedulingListResponse, BookingResponse } from '../../../shared-features/scheduling/api/schedulingApi';

export interface UseHomeDataResult {
    profile: StudentProfileResponse | undefined;
    upcomingLessons: BookingResponse[];
    nextLesson: BookingResponse | undefined;
    isLoading: boolean;
    isError: boolean;
    error: Error | null;
    refetch: () => Promise<any>;
}

/**
 * Hook principal para obter os dados necessários para a Home do aluno.
 */
export function useHomeData(): UseHomeDataResult {
    // 1. Busca perfil do aluno
    const profileQuery = useQuery<StudentProfileResponse, Error>({
        queryKey: ['student', 'profile'],
        queryFn: getHomeProfile,
        staleTime: 1000 * 60 * 5, // 5 minutos
    });

    // 2. Busca próximas aulas confirmadas
    const lessonsQuery = useQuery<SchedulingListResponse, Error>({
        queryKey: ['student', 'lessons', 'upcoming'],
        queryFn: getUpcomingLessons,
        staleTime: 1000 * 60 * 2, // 2 minutos
    });

    const upcomingLessons = lessonsQuery.data?.schedulings || [];

    // A próxima aula é a primeira da lista (assumindo que o baceknd já ordena por data)
    const nextLesson = upcomingLessons.length > 0 ? upcomingLessons[0] : undefined;

    const isLoading = profileQuery.isLoading || lessonsQuery.isLoading;
    const isError = profileQuery.isError || lessonsQuery.isError;
    const error = profileQuery.error || lessonsQuery.error;

    const refetch = async () => {
        await Promise.all([
            profileQuery.refetch(),
            lessonsQuery.refetch(),
        ]);
    };

    return {
        profile: profileQuery.data,
        upcomingLessons,
        nextLesson,
        isLoading,
        isError,
        error,
        refetch,
    };
}
