import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getDisputes, getDisputeById, updateDisputeStatus, resolveDispute } from '@/services/disputes.service';
import { AdminDisputeFilters, ResolveDisputeData } from '@/types/dispute';

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

export const useUpdateDisputeStatus = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, status }: { id: string; status: string }) =>
            updateDisputeStatus(id, status),
        onSuccess: (_, { id }) => {
            queryClient.invalidateQueries({ queryKey: ['admin_dispute', id] });
            queryClient.invalidateQueries({ queryKey: ['admin_disputes'] });
        },
    });
};

export const useResolveDispute = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: string; data: ResolveDisputeData }) =>
            resolveDispute(id, data),
        onSuccess: (_, { id }) => {
            queryClient.invalidateQueries({ queryKey: ['admin_dispute', id] });
            queryClient.invalidateQueries({ queryKey: ['admin_disputes'] });
        },
    });
};
