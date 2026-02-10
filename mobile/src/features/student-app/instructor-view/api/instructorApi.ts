/**
 * GoDrive Mobile - Instructor View API
 *
 * API functions para visualização de perfil de instrutor pelo aluno.
 */

import api, { SHARED_API } from '../../../../lib/axios';

// === Tipos ===

export interface Location {
    latitude: number;
    longitude: number;
}

export interface PublicReview {
    rating: number;
    comment: string | null;
    student_name: string;
    created_at: string;
}

export interface InstructorDetail {
    id: string;
    user_id: string;
    name: string;
    bio: string;
    vehicle_type: string;
    license_category: string;
    hourly_rate: number;
    rating: number;
    total_reviews: number;
    is_available: boolean;
    location: Location | null;
    avatar_url?: string;
    reviews: PublicReview[];
}

// === Funções de API ===

/**
 * Busca detalhes completos de um instrutor específico pelo ID.
 */
export async function getInstructorById(instructorId: string): Promise<InstructorDetail> {
    const response = await api.get<InstructorDetail>(`${SHARED_API}/instructors/${instructorId}`);
    return response.data;
}
