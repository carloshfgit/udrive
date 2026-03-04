/**
 * useInstructorDashboard Hook
 *
 * Hook consolidado para os dados da tela de Dashboard do instrutor.
 * Busca em paralelo: earnings, reviews e aulas recentes concluídas.
 */

import { useQuery } from '@tanstack/react-query';
import { getInstructorEarnings } from '../api/paymentApi';
import { getInstructorReviews } from '../api/instructorApi';
import { getInstructorSchedule } from '../api/scheduleApi';

export const INSTRUCTOR_DASHBOARD_QUERY_KEY = ['instructor', 'dashboard'];

/**
 * Hook principal para os dados do Dashboard do Instrutor.
 */
export function useInstructorDashboard() {
    const earningsQuery = useQuery({
        queryKey: [...INSTRUCTOR_DASHBOARD_QUERY_KEY, 'earnings'],
        queryFn: getInstructorEarnings,
        staleTime: 2 * 60 * 1000, // 2 minutos
    });

    const reviewsQuery = useQuery({
        queryKey: [...INSTRUCTOR_DASHBOARD_QUERY_KEY, 'reviews'],
        queryFn: getInstructorReviews,
        staleTime: 5 * 60 * 1000, // 5 minutos
    });

    const recentLessonsQuery = useQuery({
        queryKey: [...INSTRUCTOR_DASHBOARD_QUERY_KEY, 'recent-lessons'],
        queryFn: () => getInstructorSchedule({ status_filter: 'completed', limit: 5 }),
        staleTime: 2 * 60 * 1000,
    });

    const isLoading =
        earningsQuery.isLoading ||
        reviewsQuery.isLoading ||
        recentLessonsQuery.isLoading;

    const isError =
        earningsQuery.isError ||
        reviewsQuery.isError ||
        recentLessonsQuery.isError;

    const refetch = async () => {
        await Promise.all([
            earningsQuery.refetch(),
            reviewsQuery.refetch(),
            recentLessonsQuery.refetch(),
        ]);
    };

    return {
        earnings: earningsQuery.data,
        reviews: reviewsQuery.data,
        recentLessons: recentLessonsQuery.data?.schedulings ?? [],
        isLoading,
        isError,
        refetch,
    };
}
