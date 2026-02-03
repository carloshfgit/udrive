/**
 * Instructor Profile API
 *
 * Funções para comunicação com endpoints de perfil do instrutor.
 */

import api, { INSTRUCTOR_API } from '../../../lib/axios';

// ============= Types =============

export interface InstructorProfile {
    id: string;
    user_id: string;
    bio: string;
    vehicle_type: string;
    license_category: string;
    hourly_rate: number;
    rating: number;
    total_reviews: number;
    is_available: boolean;
    full_name: string;
    phone?: string | null;
    cpf?: string | null;
    birth_date?: string | null;
    location: LocationData | null;
    distance_km?: number;
}

export interface LocationData {
    latitude: number;
    longitude: number;
}

export interface UpdateInstructorProfileRequest {
    bio?: string;
    vehicle_type?: string;
    license_category?: string;
    hourly_rate?: number;
    is_available?: boolean;
    full_name?: string;
    phone?: string;
    cpf?: string;
    birth_date?: string | null;
    latitude?: number;
    longitude?: number;
}

// ============= API Functions =============

/**
 * Obtém o perfil do instrutor autenticado.
 * Retorna null se o perfil ainda não foi criado (404).
 */
export async function getInstructorProfile(): Promise<InstructorProfile | null> {
    try {
        const response = await api.get<InstructorProfile>(`${INSTRUCTOR_API}/profile`);
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
 * Atualiza o perfil do instrutor.
 * O backend cria o perfil automaticamente se não existir via PUT.
 */
export async function updateInstructorProfile(
    data: UpdateInstructorProfileRequest
): Promise<InstructorProfile> {
    const response = await api.put<InstructorProfile>(`${INSTRUCTOR_API}/profile`, data);
    return response.data;
}
