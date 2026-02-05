import { useQuery } from '@tanstack/react-query';
import { getStudentSchedulings } from '../api/schedulingApi';

interface UseStudentSchedulingsOptions {
    status?: string;
    page?: number;
    limit?: number;
    enabled?: boolean;
}

export function useStudentSchedulings({
    status,
    page = 1,
    limit = 10,
    enabled = true,
}: UseStudentSchedulingsOptions = {}) {
    return useQuery({
        queryKey: ['student-schedulings', { status, page, limit }],
        queryFn: () => getStudentSchedulings(status, page, limit),
        enabled,
    });
}
