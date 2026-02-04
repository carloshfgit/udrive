/**
 * GoDrive Mobile - useAvailableTimeSlots Hook
 *
 * Hook para buscar horários disponíveis para uma data específica.
 */

import { useQuery } from '@tanstack/react-query';
import { getAvailableTimeSlots, AvailableTimeSlotsResponse } from '../api/schedulingApi';

/**
 * Hook para buscar horários disponíveis em uma data específica.
 *
 * @param instructorId - ID do instrutor
 * @param date - Data no formato YYYY-MM-DD
 * @param durationMinutes - Duração da aula em minutos (default: 60)
 * @returns Query result com horários disponíveis
 */
export function useAvailableTimeSlots(
    instructorId: string,
    date: string | null,
    durationMinutes: number = 60
) {
    return useQuery<AvailableTimeSlotsResponse, Error>({
        queryKey: ['instructor', 'available-slots', instructorId, date, durationMinutes],
        queryFn: () => getAvailableTimeSlots(instructorId, date!, durationMinutes),
        enabled: !!instructorId && !!date,
        staleTime: 1 * 60 * 1000, // 1 minuto (menor que availability pois pode mudar)
    });
}
