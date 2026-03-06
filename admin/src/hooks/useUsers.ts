import { useQuery } from '@tanstack/react-query';
import { getUsers } from '@/services/users.service';
import { AdminUserFilters } from '@/types/user';

export const useUsers = (filters: AdminUserFilters) => {
    return useQuery({
        queryKey: ['admin_users', filters],
        queryFn: () => getUsers(filters),
        placeholderData: (previousData) => previousData, // keep previous data while fetching new page
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
};
