/**
 * GoDrive Mobile - Scheduling API
 *
 * Funções para consumir a API de agendamento de aulas.
 */

import api, { STUDENT_API } from '../../../../lib/axios';

// === Tipos ===

export interface AvailabilitySlot {
    id: string;
    instructor_id: string;
    day_of_week: number;
    day_name: string;
    start_time: string;
    end_time: string;
    is_active: boolean;
    duration_minutes: number;
}

export interface AvailabilityListResponse {
    availabilities: AvailabilitySlot[];
    instructor_id: string;
    total_count: number;
}

export interface TimeSlot {
    start_time: string;
    end_time: string;
    is_available: boolean;
}

export interface AvailableTimeSlotsResponse {
    instructor_id: string;
    date: string;
    time_slots: TimeSlot[];
    total_available: number;
}

export interface CreateBookingRequest {
    instructor_id: string;
    scheduled_datetime: string; // ISO 8601 format
    duration_minutes: number;
}

export interface BookingResponse {
    id: string;
    student_id: string;
    instructor_id: string;
    scheduled_datetime: string;
    duration_minutes: number;
    price: number;
    status: string;
    created_at: string;
    student_name?: string;
    instructor_name?: string;
}

// === Funções de API ===

/**
 * Busca a disponibilidade semanal de um instrutor.
 */
export async function getInstructorAvailability(
    instructorId: string
): Promise<AvailabilityListResponse> {
    const response = await api.get<AvailabilityListResponse>(
        `${STUDENT_API}/instructors/${instructorId}/availability`
    );
    return response.data;
}

/**
 * Busca os horários disponíveis para uma data específica.
 */
export async function getAvailableTimeSlots(
    instructorId: string,
    date: string,
    durationMinutes: number = 60
): Promise<AvailableTimeSlotsResponse> {
    const response = await api.get<AvailableTimeSlotsResponse>(
        `${STUDENT_API}/instructors/${instructorId}/available-slots`,
        {
            params: {
                target_date: date,
                duration_minutes: durationMinutes,
            },
        }
    );
    return response.data;
}

/**
 * Cria um novo agendamento de aula.
 */
export async function createBooking(
    data: CreateBookingRequest
): Promise<BookingResponse> {
    const response = await api.post<BookingResponse>(
        `${STUDENT_API}/lessons`,
        data
    );
    return response.data;
}
