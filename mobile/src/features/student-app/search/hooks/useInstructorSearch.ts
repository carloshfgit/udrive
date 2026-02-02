/**
 * GoDrive Mobile - Instructor Search Hooks
 *
 * Custom hooks para gerenciar estado de busca de instrutores.
 */

import { useQuery } from '@tanstack/react-query';
import { useState, useEffect, useCallback } from 'react';
import * as Location from 'expo-location';
import { searchInstructors, SearchInstructorsParams, SearchInstructorsResponse, Instructor } from '../api/searchApi';

// === Tipos ===

export interface SearchFilters {
    category?: string;
    minRating?: number;
    minPrice?: number;
    maxPrice?: number;
    radiusKm?: number;
}

export interface UserLocation {
    latitude: number;
    longitude: number;
}

export interface UseUserLocationResult {
    location: UserLocation | null;
    isLoading: boolean;
    error: string | null;
    requestPermission: () => Promise<void>;
}

export interface UseInstructorSearchResult {
    instructors: Instructor[];
    isLoading: boolean;
    isError: boolean;
    error: Error | null;
    refetch: () => void;
    totalCount: number;
}

// === Hooks ===

/**
 * Hook para obter e gerenciar a localização do usuário.
 */
export function useUserLocation(): UseUserLocationResult {
    const [location, setLocation] = useState<UserLocation | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const requestPermission = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const { status } = await Location.requestForegroundPermissionsAsync();

            if (status !== 'granted') {
                setError('Permissão de localização negada');
                setIsLoading(false);
                return;
            }

            const currentLocation = await Location.getCurrentPositionAsync({
                accuracy: Location.Accuracy.Balanced,
            });

            setLocation({
                latitude: currentLocation.coords.latitude,
                longitude: currentLocation.coords.longitude,
            });
        } catch (err) {
            setError('Erro ao obter localização');
            console.error('Location error:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        requestPermission();
    }, [requestPermission]);

    return { location, isLoading, error, requestPermission };
}

/**
 * Hook principal para busca de instrutores com TanStack Query.
 */
export function useInstructorSearch(
    location: UserLocation | null,
    filters: SearchFilters = {}
): UseInstructorSearchResult {
    const params: SearchInstructorsParams | null = location
        ? {
            latitude: location.latitude,
            longitude: location.longitude,
            radiusKm: filters.radiusKm || 10,
            category: filters.category,
            minRating: filters.minRating,
            minPrice: filters.minPrice,
            maxPrice: filters.maxPrice,
        }
        : null;

    const query = useQuery<SearchInstructorsResponse, Error>({
        queryKey: ['instructors', 'search', params],
        queryFn: () => {
            if (!params) {
                throw new Error('Localização não disponível');
            }
            return searchInstructors(params);
        },
        enabled: !!location,
        staleTime: 1000 * 60 * 5, // 5 minutos
        gcTime: 1000 * 60 * 10, // 10 minutos (anteriormente cacheTime)
    });

    return {
        instructors: query.data?.instructors || [],
        isLoading: query.isLoading,
        isError: query.isError,
        error: query.error,
        refetch: query.refetch,
        totalCount: query.data?.total_count || 0,
    };
}

/**
 * Hook para gerenciar filtros de busca.
 */
export function useSearchFilters(initialFilters: SearchFilters = {}) {
    const [filters, setFilters] = useState<SearchFilters>(initialFilters);

    const updateFilter = useCallback(<K extends keyof SearchFilters>(
        key: K,
        value: SearchFilters[K]
    ) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    }, []);

    const resetFilters = useCallback(() => {
        setFilters(initialFilters);
    }, [initialFilters]);

    const hasActiveFilters = Object.values(filters).some(v => v !== undefined && v !== null);

    return {
        filters,
        setFilters,
        updateFilter,
        resetFilters,
        hasActiveFilters,
    };
}
