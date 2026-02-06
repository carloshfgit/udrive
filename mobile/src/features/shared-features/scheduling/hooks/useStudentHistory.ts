import { useQuery } from '@tanstack/react-query';
import { getStudentSchedulings } from '../api/schedulingApi';

interface UseStudentHistoryOptions {
    page?: number;
    limit?: number;
    enabled?: boolean;
}

export function useStudentHistory({
    page = 1,
    limit = 20,
    enabled = true,
}: UseStudentHistoryOptions = {}) {
    return useQuery({
        queryKey: ['student-history', { page, limit }],
        queryFn: () => getStudentSchedulings('completed,cancelled', page, limit),
        enabled,
    });
}
