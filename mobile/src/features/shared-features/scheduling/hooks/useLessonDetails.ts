import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getStudentSchedulings, startBooking, completeBooking, cancelBooking } from '../api/schedulingApi';

export function useLessonDetails(schedulingId: string) {
    const queryClient = useQueryClient();

    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ['scheduling', schedulingId],
        queryFn: async () => {
            const response = await getStudentSchedulings();
            const found = response.schedulings.find(s => s.id === schedulingId);
            if (!found) {
                // Try history if not found in active lessons
                // (Optional, but good for robust navigation)
            }
            if (!found) throw new Error('Agendamento não encontrado');
            return found;
        }
    });

    const startMutation = useMutation({
        mutationFn: () => startBooking(schedulingId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scheduling', schedulingId] });
            queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
        }
    });

    const completeMutation = useMutation({
        mutationFn: () => completeBooking(schedulingId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scheduling', schedulingId] });
            queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
            queryClient.invalidateQueries({ queryKey: ['student-history'] });
        }
    });

    const cancelMutation = useMutation({
        mutationFn: (reason?: string) => cancelBooking(schedulingId, reason),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scheduling', schedulingId] });
            queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
            queryClient.invalidateQueries({ queryKey: ['student-history'] });
        }
    });

    return {
        lesson: data,
        isLoading,
        isError,
        refetch,
        startLesson: startMutation.mutate,
        isStarting: startMutation.isPending,
        completeLesson: completeMutation.mutate,
        isCompleting: completeMutation.isPending,
        cancelLesson: cancelMutation.mutate,
        isCancelling: cancelMutation.isPending
    };
}
