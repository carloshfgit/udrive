/**
 * Profile API
 *
 * Funções para comunicação com endpoints de perfil do aluno.
 */

import api, { STUDENT_API } from '../../../lib/axios';

// ============= Types =============

export interface StudentProfile {
    id: string;
    user_id: string;
    preferred_schedule: string;
    license_category_goal: string;
    learning_stage: string;
    notes: string;
    total_lessons: number;
    phone: string;
    cpf: string;
    birth_date: string | null; // ISO date format YYYY-MM-DD
}

export interface UpdateStudentProfileRequest {
    preferred_schedule?: string;
    license_category_goal?: string;
    learning_stage?: string;
    notes?: string;
    phone?: string;
    cpf?: string;
    birth_date?: string | null; // ISO date format YYYY-MM-DD
}

export interface LocationData {
    latitude: number;
    longitude: number;
}

// ============= API Functions =============

/**
 * Obtém o perfil do aluno autenticado.
 * Retorna null se o perfil ainda não foi criado (404).
 */
export async function getStudentProfile(): Promise<StudentProfile | null> {
    try {
        const response = await api.get<StudentProfile>(`${STUDENT_API}/profile`);
        return response.data;
    } catch (error: unknown) {
        // 404 significa que o perfil ainda não foi criado - retornar null
        if (
            error &&
            typeof error === 'object' &&
            'response' in error &&
            (error as { response?: { status?: number } }).response?.status === 404
        ) {
            return null;
        }
        throw error;
    }
}

/**
 * Atualiza o perfil do aluno.
 * Nota: O backend cria o perfil automaticamente se não existir via PUT.
 */
export async function updateStudentProfile(
    data: UpdateStudentProfileRequest
): Promise<StudentProfile> {
    const response = await api.put<StudentProfile>(`${STUDENT_API}/profile`, data);
    return response.data;
}

/**
 * Atualiza a localização do aluno.
 * Nota: A localização é armazenada localmente via useLocationStore.
 * Esta função envia ao backend se houver endpoint disponível.
 */
export async function updateLocation(location: LocationData): Promise<void> {
    // Nota: O backend pode não ter endpoint específico para localização do aluno.
    // A localização é usada principalmente para busca de instrutores.
    // Por ora, apenas log para debug - implementar quando endpoint estiver disponível.
    console.log('[profileApi] Location updated:', location);
    // Futuro: await api.put(`${STUDENT_API}/location`, location);
}
