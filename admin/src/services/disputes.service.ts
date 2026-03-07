import api from '@/lib/api';
import { Dispute, DisputePayment, AdminDisputeFilters, ResolveDisputeData } from '@/types/dispute';
import { PaginatedResponse } from '@/types/api';

export const getDisputes = async (
    filters: AdminDisputeFilters
): Promise<PaginatedResponse<Dispute>> => {
    const params = new URLSearchParams();

    params.append('page', filters.page.toString());
    params.append('limit', filters.size.toString());

    if (filters.status && filters.status !== 'all') {
        params.append('status', filters.status);
    }

    const { data } = await api.get<any>(
        `/admin/disputes?${params.toString()}`
    );

    // Adaptando para o formato PaginatedResponse esperado pelo frontend padrão
    return {
        items: data.disputes || [],
        total: data.total_count || 0,
        page: filters.page,
        size: data.limit || filters.size,
        pages: Math.ceil((data.total_count || 0) / (data.limit || filters.size)) || 1,
    };
};

export const getDisputeById = async (id: string): Promise<Dispute> => {
    const { data } = await api.get<Dispute>(`/admin/disputes/${id}`);
    return data;
};

export const getDisputePayments = async (disputeId: string): Promise<DisputePayment[]> => {
    const { data } = await api.get<{ payments: DisputePayment[] }>(
        `/admin/disputes/${disputeId}/payments`
    );
    return data.payments;
};

export const updateDisputeStatus = async (id: string, status: string): Promise<Dispute> => {
    const { data } = await api.patch<Dispute>(`/admin/disputes/${id}/status`, {
        new_status: status,
    });
    return data;
};

export const resolveDispute = async (id: string, data: ResolveDisputeData): Promise<Dispute> => {
    const { data: responseData } = await api.post<Dispute>(`/admin/disputes/${id}/resolve`, data);
    return responseData;
};
