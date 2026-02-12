/**
 * GoDrive Mobile - Student Home Hooks
 * 
 * Custom hooks para gerenciar os dados da Home do aluno.
 */

import { useQuery } from '@tanstack/react-query';
import { getHomeProfile, getUpcomingLessons, getNextLesson, StudentProfileResponse } from '../api/homeApi';
import { SchedulingListResponse, BookingResponse } from '../../../shared-features/scheduling/api/schedulingApi';

export interface UseHomeDataResult {
    profile: StudentProfileResponse | undefined;
    upcomingLessons: BookingResponse[];
    nextLesson: BookingResponse | null | undefined;
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

    // 2. Busca próximas aulas confirmadas (para lista)
    const lessonsQuery = useQuery<SchedulingListResponse, Error>({
        queryKey: ['student', 'lessons', 'upcoming'],
        queryFn: getUpcomingLessons,
        staleTime: 1000 * 60 * 2, // 2 minutos
    });

    // 3. Busca a aula MAIS próxima (especificamente para o card da Home)
    const nextLessonQuery = useQuery<BookingResponse | null, Error>({
        queryKey: ['student', 'lessons', 'next'],
        queryFn: getNextLesson,
        staleTime: 1000 * 60 * 2, // 2 minutos
    });

    const upcomingLessons = lessonsQuery.data?.schedulings || [];
    const nextLesson = nextLessonQuery.data;

    const isLoading = profileQuery.isLoading || lessonsQuery.isLoading || nextLessonQuery.isLoading;
    const isError = profileQuery.isError || lessonsQuery.isError || nextLessonQuery.isError;
    const error = profileQuery.error || lessonsQuery.error || nextLessonQuery.error;

    const refetch = async () => {
        await Promise.all([
            profileQuery.refetch(),
            lessonsQuery.refetch(),
            nextLessonQuery.refetch(),
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
