import api from "@/lib/api";
import { Scheduling, SchedulingFilters, SchedulingListResponse } from "@/types/scheduling";

export const schedulingsService = {
  getSchedulings: async (filters: SchedulingFilters = {}): Promise<SchedulingListResponse> => {
    const { page = 1, limit = 10, ...otherFilters } = filters;
    
    // Converte filtros para query params
    const params = new URLSearchParams();
    params.append("page", page.toString());
    params.append("limit", limit.toString());
    
    Object.entries(otherFilters).forEach(([key, value]) => {
      if (value) {
        params.append(key, value.toString());
      }
    });

    const response = await api.get<SchedulingListResponse>(`/admin/schedulings?${params.toString()}`);
    return response.data;
  },

  getSchedulingById: async (id: string): Promise<Scheduling> => {
    const response = await api.get<Scheduling>(`/admin/schedulings/${id}`);
    return response.data;
  },

  cancelScheduling: async (id: string, reason: string): Promise<Scheduling> => {
    const response = await api.patch<Scheduling>(`/admin/schedulings/${id}/cancel`, { reason });
    return response.data;
  }
};
