/**
 * GoDrive Mobile - Scheduling API
 *
 * Funções para consumir a API de agendamento de aulas.
 */

import api, { STUDENT_API, SHARED_API } from '../../../../lib/axios';

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
    instructor_rating?: number;
    instructor_review_count?: number;
    has_review?: boolean;
    started_at?: string;
    student_confirmed_at?: string;
    rescheduled_datetime?: string;
    rescheduled_by?: string;
}

export interface SchedulingListResponse {
    schedulings: BookingResponse[];
    total_count: number;
    limit: number;
    offset: number;
    has_more: boolean;
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

/**
 * Busca a lista de agendamentos do aluno logado.
 */
export async function getStudentSchedulings(
    status?: string,
    page: number = 1,
    limit: number = 10
): Promise<SchedulingListResponse> {
    const response = await api.get<SchedulingListResponse>(
        `${STUDENT_API}/lessons`,
        {
            params: {
                status_filter: status,
                page,
                limit,
            },
        }
    );
    return response.data;
}

/**
 * Busca os detalhes de um agendamento específico.
 */
export async function getBooking(
    schedulingId: string
): Promise<BookingResponse> {
    const response = await api.get<BookingResponse>(
        `${STUDENT_API}/lessons/${schedulingId}`
    );
    return response.data;
}

/**
 * Registra o início de uma aula.
 */
export async function startBooking(
    schedulingId: string
): Promise<BookingResponse> {
    const response = await api.post<BookingResponse>(
        `${STUDENT_API}/lessons/${schedulingId}/start`
    );
    return response.data;
}

/**
 * Marca uma aula como concluída.
 */
export async function completeBooking(
    schedulingId: string
): Promise<BookingResponse> {
    const response = await api.post<BookingResponse>(
        `${STUDENT_API}/lessons/${schedulingId}/complete`
    );
    return response.data;
}

/**
 * Cancela um agendamento.
 */
export async function cancelBooking(
    schedulingId: string,
    reason?: string
): Promise<any> {
    const response = await api.post(
        `${STUDENT_API}/lessons/${schedulingId}/cancel`,
        { reason }
    );
    return response.data;
}

/**
 * Adiciona uma avaliação para uma aula concluída.
 */
export async function createReview(
    schedulingId: string,
    rating: number,
    comment?: string
): Promise<any> {
    const response = await api.post(
        `${STUDENT_API}/lessons/${schedulingId}/review`,
        { rating, comment }
    );
    return response.data;
}

/**
 * Solicita o reagendamento de uma aula.
 */
export async function requestReschedule(
    schedulingId: string,
    newDatetime: string
): Promise<BookingResponse> {
    const response = await api.post<BookingResponse>(
        `${STUDENT_API}/lessons/${schedulingId}/request-reschedule`,
        { new_datetime: newDatetime }
    );
    return response.data;
}

/**
 * Responde a uma solicitação de reagendamento (ação do aluno).
 */
export async function respondReschedule(
    schedulingId: string,
    accepted: boolean
): Promise<BookingResponse> {
    const response = await api.post<BookingResponse>(
        `${STUDENT_API}/lessons/${schedulingId}/respond-reschedule`,
        { accepted }
    );
    return response.data;
}
