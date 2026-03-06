import { useQuery } from '@tanstack/react-query';
import { getDisputes, getDisputeById } from '@/services/disputes.service';
import { AdminDisputeFilters } from '@/types/dispute';

export const useDisputes = (filters: AdminDisputeFilters) => {
    return useQuery({
        queryKey: ['admin_disputes', filters],
        queryFn: () => getDisputes(filters),
        placeholderData: (previousData) => previousData,
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
};

export const useDispute = (id: string, enabled: boolean = true) => {
    return useQuery({
        queryKey: ['admin_dispute', id],
        queryFn: () => getDisputeById(id),
        enabled: !!id && enabled,
    });
};
