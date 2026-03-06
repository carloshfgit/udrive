import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getUserById, toggleUserStatus } from "@/services/users.service";
import { User } from "@/types/user";

export function useUser(userId: string) {
    const queryClient = useQueryClient();

    const query = useQuery({
        queryKey: ["user", userId],
        queryKeyHashFn: () => `user-${userId}`,
        queryFn: () => getUserById(userId),
        enabled: !!userId,
    });

    const toggleStatusMutation = useMutation({
        mutationFn: () => toggleUserStatus(userId),
        onSuccess: (data) => {
            queryClient.setQueryData(["user", userId], data);
            queryClient.invalidateQueries({ queryKey: ["users"] });
        },
    });

    return {
        user: query.data,
        isLoading: query.isLoading,
        isError: query.isError,
        isTogglingStatus: toggleStatusMutation.isPending,
        toggleStatus: toggleStatusMutation.mutate,
    };
}
