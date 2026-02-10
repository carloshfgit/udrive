import { useQuery } from '@tanstack/react-query';
import { getUnreadCount } from '../api/chatApi';

export function useUnreadCount() {
    const query = useQuery({
        queryKey: ['chat-unread-count'],
        queryFn: getUnreadCount,
        refetchInterval: 30000,
    });

    return {
        ...query,
        unreadCount: query.data?.unread_count ?? 0,
    };
}
