/**
 * useInstructorSchedule Hook
 *
 * TanStack Query hooks para gerenciamento de agenda do instrutor.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
    getScheduleByDate,
    getInstructorSchedule,
    confirmScheduling,
    completeScheduling,
    cancelScheduling,
    getSchedulingDates,
    SchedulingStatus,
} from '../api/scheduleApi';

// Query keys
export const INSTRUCTOR_SCHEDULE_QUERY_KEY = ['instructor', 'schedule'];

/**
 * Hook para buscar agendamentos de uma data específica.
 */
export function useScheduleByDate(date: string) {
    return useQuery({
        queryKey: [...INSTRUCTOR_SCHEDULE_QUERY_KEY, 'by-date', date],
        queryFn: () => getScheduleByDate(date),
        staleTime: 2 * 60 * 1000, // 2 minutos
        enabled: !!date,
    });
}

/**
 * Hook para buscar todos os agendamentos com paginação.
 */
export function useInstructorSchedule(params?: {
    status_filter?: SchedulingStatus;
    page?: number;
    limit?: number;
}) {
    return useQuery({
        queryKey: [...INSTRUCTOR_SCHEDULE_QUERY_KEY, 'list', params],
        queryFn: () => getInstructorSchedule(params),
        staleTime: 2 * 60 * 1000, // 2 minutos
    });
}

/**
 * Hook para confirmar um agendamento.
 */
export function useConfirmScheduling() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (schedulingId: string) => confirmScheduling(schedulingId),
        onSuccess: () => {
            // Invalidar cache da agenda para recarregar
            queryClient.invalidateQueries({ queryKey: INSTRUCTOR_SCHEDULE_QUERY_KEY });
        },
    });
}

/**
 * Hook para marcar agendamento como concluído.
 */
export function useCompleteScheduling() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (schedulingId: string) => completeScheduling(schedulingId),
        onSuccess: () => {
            // Invalidar cache da agenda para recarregar
            queryClient.invalidateQueries({ queryKey: INSTRUCTOR_SCHEDULE_QUERY_KEY });
        },
    });
}

/**
 * Hook para cancelar um agendamento.
 */
export function useCancelScheduling() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ schedulingId, reason }: { schedulingId: string; reason?: string }) =>
            cancelScheduling(schedulingId, reason),
        onSuccess: () => {
            // Invalidar cache da agenda para recarregar
            queryClient.invalidateQueries({ queryKey: INSTRUCTOR_SCHEDULE_QUERY_KEY });
        },
    });
}

/**
 * Hook para buscar datas com agendamentos no mês.
 */
export function useSchedulingDates(year: number, month: number) {
    return useQuery({
        queryKey: [...INSTRUCTOR_SCHEDULE_QUERY_KEY, 'dates', year, month],
        queryFn: () => getSchedulingDates(year, month),
        staleTime: 5 * 60 * 1000, // 5 minutos
        enabled: year > 0 && month > 0,
    });
}

