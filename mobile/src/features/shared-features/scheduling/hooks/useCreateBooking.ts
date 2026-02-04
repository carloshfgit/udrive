/**
 * GoDrive Mobile - useCreateBooking Hook
 *
 * Hook de mutation para criar um agendamento de aula.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createBooking, CreateBookingRequest, BookingResponse } from '../api/schedulingApi';

/**
 * Hook para criar um novo agendamento de aula.
 *
 * Após sucesso, invalida queries relacionadas a agendamentos.
 *
 * @returns Mutation para criar agendamento
 */
export function useCreateBooking() {
    const queryClient = useQueryClient();

    return useMutation<BookingResponse, Error, CreateBookingRequest>({
        mutationFn: createBooking,
        onSuccess: (data) => {
            // Invalidar lista de agendamentos do aluno
            queryClient.invalidateQueries({ queryKey: ['student', 'lessons'] });
            // Invalidar horários disponíveis do instrutor
            queryClient.invalidateQueries({
                queryKey: ['instructor', 'available-slots', data.instructor_id],
            });
        },
    });
}
