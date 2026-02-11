/**
 * Schedule & Availability API
 *
 * Funções para comunicação com endpoints de agenda e disponibilidade do instrutor.
 */

import api, { INSTRUCTOR_API } from '../../../lib/axios';

// ============= Types =============

export type SchedulingStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'reschedule_requested';

export interface Scheduling {
    id: string;
    student_id: string;
    instructor_id: string;
    scheduled_datetime: string;
    duration_minutes: number;
    price: number;
    status: SchedulingStatus;
    cancellation_reason?: string | null;
    cancelled_by?: string | null;
    cancelled_at?: string | null;
    completed_at?: string | null;
    started_at?: string | null;
    student_confirmed_at?: string | null;
    created_at: string;
    student_name?: string | null;
    instructor_name?: string | null;
    rescheduled_datetime?: string | null;
    rescheduled_by?: string | null;
}

export interface SchedulingListResponse {
    schedulings: Scheduling[];
    total_count: number;
    limit: number;
    offset: number;
    has_more: boolean;
}

export interface Availability {
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
    availabilities: Availability[];
    instructor_id: string;
    total_count: number;
}

export interface CreateAvailabilityRequest {
    day_of_week: number;
    start_time: string; // HH:MM
    end_time: string;   // HH:MM
}

// ============= Schedule API Functions =============

/**
 * Busca agendamentos do instrutor para uma data específica.
 */
export async function getScheduleByDate(date: string): Promise<SchedulingListResponse> {
    const response = await api.get<SchedulingListResponse>(
        `${INSTRUCTOR_API}/schedule/by-date`,
        { params: { date } }
    );
    return response.data;
}

/**
 * Busca todos os agendamentos do instrutor com paginação.
 */
export async function getInstructorSchedule(params?: {
    status_filter?: SchedulingStatus;
    page?: number;
    limit?: number;
}): Promise<SchedulingListResponse> {
    const response = await api.get<SchedulingListResponse>(
        `${INSTRUCTOR_API}/schedule`,
        { params }
    );
    return response.data;
}

/**
 * Confirma um agendamento pendente.
 */
export async function confirmScheduling(schedulingId: string): Promise<Scheduling> {
    const response = await api.post<Scheduling>(
        `${INSTRUCTOR_API}/schedule/${schedulingId}/confirm`
    );
    return response.data;
}

/**
 * Marca um agendamento como concluído.
 */
export async function completeScheduling(schedulingId: string): Promise<Scheduling> {
    const response = await api.post<Scheduling>(
        `${INSTRUCTOR_API}/schedule/${schedulingId}/complete`
    );
    return response.data;
}

/**
 * Resultado do cancelamento de agendamento.
 */
export interface CancellationResult {
    scheduling_id: string;
    status: SchedulingStatus;
    refund_percentage: number;
    refund_amount: number;
    cancelled_at: string;
}

/**
 * Cancela um agendamento pendente ou confirmado.
 */
export async function cancelScheduling(
    schedulingId: string,
    reason?: string
): Promise<CancellationResult> {
    const response = await api.post<CancellationResult>(
        `${INSTRUCTOR_API}/schedule/${schedulingId}/cancel`,
        null,
        { params: { reason } }
    );
    return response.data;
}

/**
 * Resposta da busca de datas com agendamentos.
 */
export interface SchedulingDatesResponse {
    dates: string[];  // Array de datas no formato 'YYYY-MM-DD'
    year: number;
    month: number;
}

/**
 * Busca datas com agendamentos para um mês específico.
 */
export async function getSchedulingDates(
    year: number,
    month: number
): Promise<SchedulingDatesResponse> {
    const response = await api.get<SchedulingDatesResponse>(
        `${INSTRUCTOR_API}/schedule/dates-with-schedulings`,
        { params: { year, month } }
    );
    return response.data;
}

// ============= Availability API Functions =============

/**
 * Lista todas as disponibilidades do instrutor.
 */
export async function getAvailabilities(): Promise<AvailabilityListResponse> {
    const response = await api.get<AvailabilityListResponse>(
        `${INSTRUCTOR_API}/availability`
    );
    return response.data;
}

/**
 * Cria um novo slot de disponibilidade.
 */
export async function createAvailability(
    data: CreateAvailabilityRequest
): Promise<Availability> {
    const response = await api.post<Availability>(
        `${INSTRUCTOR_API}/availability`,
        data
    );
    return response.data;
}

/**
 * Remove um slot de disponibilidade.
 */
export async function deleteAvailability(availabilityId: string): Promise<void> {
    await api.delete(`${INSTRUCTOR_API}/availability/${availabilityId}`);
}

/**
 * Responde a uma solicitação de reagendamento.
 */
export async function respondReschedule(
    schedulingId: string,
    accepted: boolean
): Promise<Scheduling> {
    const response = await api.post<Scheduling>(
        `${INSTRUCTOR_API}/schedule/${schedulingId}/respond-reschedule`,
        { accepted }
    );
    return response.data;
}

/**
 * Solicita o reagendamento de uma aula (ação do instrutor).
 */
export async function requestReschedule(
    schedulingId: string,
    newDatetime: string
): Promise<Scheduling> {
    const response = await api.post<Scheduling>(
        `${INSTRUCTOR_API}/schedule/${schedulingId}/reschedule`,
        { new_datetime: newDatetime }
    );
    return response.data;
}

