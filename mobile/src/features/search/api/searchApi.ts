/**
 * GoDrive Mobile - Search API
 *
 * Funções para consumir a API de busca de instrutores.
 */

import axios from 'axios';

// Configuração base - pode ser movida para lib/axios.ts se ainda não existir
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
});

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
    distance_km: number | null;
    // Campos adicionais para exibição (derivados de User)
    name?: string;
    avatar_url?: string;
}

export interface SearchInstructorsParams {
    latitude: number;
    longitude: number;
    radiusKm?: number;
    limit?: number;
    category?: string;
    minRating?: number;
    maxPrice?: number;
    minPrice?: number;
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
    const { latitude, longitude, radiusKm = 10, limit = 50 } = params;

    const response = await api.get<SearchInstructorsResponse>('/instructors/search', {
        params: {
            latitude,
            longitude,
            radius_km: radiusKm,
            limit,
        },
    });

    return response.data;
}

/**
 * Busca detalhes de um instrutor específico pelo ID.
 */
export async function getInstructorById(instructorId: string): Promise<Instructor> {
    const response = await api.get<Instructor>(`/instructors/${instructorId}`);
    return response.data;
}
