import { useQuery } from '@tanstack/react-query';
import { getStudentLessons } from '../api/chatApi';

export function useStudentLessons(studentId: string) {
    return useQuery({
        queryKey: ['student-lessons', studentId],
        queryFn: () => getStudentLessons(studentId),
        enabled: !!studentId,
    });
}
