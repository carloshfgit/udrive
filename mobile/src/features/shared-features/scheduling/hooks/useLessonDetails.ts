import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getStudentSchedulings, startBooking, completeBooking, cancelBooking, getBooking, requestReschedule } from '../api/schedulingApi';

export function useLessonDetails(schedulingId: string) {
    const queryClient = useQueryClient();

    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ['scheduling', schedulingId],
        queryFn: () => getBooking(schedulingId)
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

    const requestRescheduleMutation = useMutation({
        mutationFn: (newDatetime: string) => requestReschedule(schedulingId, newDatetime),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['scheduling', schedulingId] });
            queryClient.invalidateQueries({ queryKey: ['student-schedulings'] });
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
        isCancelling: cancelMutation.isPending,
        requestReschedule: requestRescheduleMutation.mutateAsync,
        isRequestingReschedule: requestRescheduleMutation.isPending
    };
}
