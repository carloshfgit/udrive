import api from '@/lib/api';
import { User, AdminUserFilters } from '@/types/user';
import { PaginatedResponse } from '@/types/api';

export const getUsers = async (
    filters: AdminUserFilters
): Promise<PaginatedResponse<User>> => {
    // Para simplificar a URL string, limpamos os nulos/indefinidos e 'all'
    const params = new URLSearchParams();

    params.append('page', filters.page.toString());
    params.append('limit', filters.size.toString());

    if (filters.q) {
        params.append('q', filters.q);
    }

    if (filters.user_type && filters.user_type !== 'all') {
        params.append('user_type', filters.user_type);
    }

    if (filters.is_active !== undefined && filters.is_active !== 'all') {
        params.append('is_active', String(filters.is_active));
    }

    const { data } = await api.get<any>(
        `/admin/users?${params.toString()}`
    );

    return {
        items: data.users || [],
        total: data.total_count || 0,
        page: filters.page,
        size: data.limit || filters.size,
        pages: Math.ceil((data.total_count || 0) / (data.limit || filters.size)) || 1,
    };
};
