/**
 * GoDrive Mobile - Search API
 *
 * Funções para consumir a API de busca de instrutores.
 */

import api, { STUDENT_API, SHARED_API } from '../../../../lib/axios';

// === Tipos ===

export interface Location {
    latitude: number;
    longitude: number;
}

export interface Instructor {
    id: string;
    user_id: string;
    bio: string;
    vehicle_type: string;
    license_category: string;
    hourly_rate: number;
    rating: number;
    total_reviews: number;
    is_available: boolean;
    location: Location | null;
    city: string | null;
    distance_km: number | null;
    // Campos adicionais para exibição (derivados de User)
    name?: string;
    full_name?: string;
    avatar_url?: string;
    price_cat_a_instructor_vehicle?: number;
    price_cat_a_student_vehicle?: number;
    price_cat_b_instructor_vehicle?: number;
    price_cat_b_student_vehicle?: number;
}

export interface SearchInstructorsParams {
    latitude: number;
    longitude: number;
    radiusKm?: number;
    limit?: number;
    category?: string;
    biological_sex?: string;
    search?: string | null;
}

export interface SearchInstructorsResponse {
    instructors: Instructor[];
    total_count: number;
    radius_km: number;
    center_latitude: number;
    center_longitude: number;
}

// === Funções de API ===

/**
 * Busca instrutores próximos à localização especificada.
 */
export async function searchInstructors(
    params: SearchInstructorsParams
): Promise<SearchInstructorsResponse> {
    const { latitude, longitude, radiusKm = 10, limit = 50, biological_sex, category } = params;

    const response = await api.get<SearchInstructorsResponse>(`${STUDENT_API}/instructors/search`, {
        params: {
            latitude,
            longitude,
            radius_km: radiusKm,
            limit,
            biological_sex,
            license_category: category,
            search: params.search,
        },
    });

    return response.data;
}

/**
 * Busca detalhes de um instrutor específico pelo ID.
 */
export async function getInstructorById(instructorId: string): Promise<Instructor> {
    const response = await api.get<Instructor>(`${SHARED_API}/instructors/${instructorId}`);
    return response.data;
}
