import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { schedulingsService } from '@/services/schedulings.service';

export const useScheduling = (id: string) => {
    const queryClient = useQueryClient();

    const query = useQuery({
        queryKey: ['admin_scheduling', id],
        queryFn: () => schedulingsService.getSchedulingById(id),
        enabled: !!id,
    });

    const cancelMutation = useMutation({
        mutationFn: ({ reason }: { reason: string }) => schedulingsService.cancelScheduling(id, reason),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin_scheduling', id] });
            queryClient.invalidateQueries({ queryKey: ['admin_schedulings'] });
        },
    });

    return {
        scheduling: query.data,
        isLoading: query.isLoading,
        isError: query.isError,
        cancelScheduling: cancelMutation.mutateAsync,
        isCancelling: cancelMutation.isPending,
    };
};
