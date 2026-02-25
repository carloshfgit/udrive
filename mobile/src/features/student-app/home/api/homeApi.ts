/**
 * GoDrive Mobile - Home API
 * 
 * Funções para consumir os dados da Home do aluno.
 */

import api, { STUDENT_API } from '../../../../lib/axios';
import { SchedulingListResponse, BookingResponse } from '../../../shared-features/scheduling/api/schedulingApi';

export interface StudentProfileResponse {
    id: string;
    user_id: string;
    preferred_schedule: string;
    license_category_goal: string;
    learning_stage: string;
    notes: string;
    total_lessons: number;
    full_name?: string;
    phone?: string;
    cpf?: string;
    birth_date?: string;
}

/**
 * Busca o perfil do aluno logado.
 */
export async function getHomeProfile(): Promise<StudentProfileResponse> {
    const response = await api.get<StudentProfileResponse>(`${STUDENT_API}/profile`);
    return response.data;
}

/**
 * Busca as próximas aulas confirmadas do aluno.
 */
export async function getUpcomingLessons(): Promise<SchedulingListResponse> {
    const response = await api.get<SchedulingListResponse>(`${STUDENT_API}/lessons`, {
        params: {
            status_filter: 'confirmed',
            payment_status_filter: 'completed',
            limit: 5,
        }
    });
    return response.data;
}

/**
 * Busca a próxima aula do aluno.
 */
export async function getNextLesson(): Promise<BookingResponse | null> {
    const response = await api.get<BookingResponse | null>(`${STUDENT_API}/lessons/next`);
    return response.data;
}
/**
 * Busca a quantidade de aulas concluídas do aluno.
 */
export async function getCompletedLessonsCount(): Promise<number> {
    const response = await api.get<SchedulingListResponse>(`${STUDENT_API}/lessons`, {
        params: {
            status_filter: 'completed',
            limit: 1,
        }
    });
    return response.data.total_count;
}
