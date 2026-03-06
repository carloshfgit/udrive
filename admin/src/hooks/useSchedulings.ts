import { useQuery } from '@tanstack/react-query';
import { schedulingsService } from '@/services/schedulings.service';
import { SchedulingFilters } from '@/types/scheduling';

export const useSchedulings = (filters: SchedulingFilters) => {
    return useQuery({
        queryKey: ['admin_schedulings', filters],
        queryFn: () => schedulingsService.getSchedulings(filters),
        placeholderData: (previousData) => previousData,
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
};
