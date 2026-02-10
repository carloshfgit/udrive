import { useQuery } from '@tanstack/react-query';
import { getStudentConversations } from '../api/chatApi';

export function useStudentConversations() {
    return useQuery({
        queryKey: ['chat-student-conversations'],
        queryFn: getStudentConversations,
        refetchInterval: 30000,
    });
}
