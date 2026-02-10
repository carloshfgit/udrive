import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@lib/store';
import { getStudentLessons, getStudentLessonsWithInstructor } from '../api/chatApi';

/**
 * Hook para buscar aulas entre dois usuários.
 * - Se o usuário logado é instrutor: busca aulas do aluno (studentId)
 * - Se o usuário logado é aluno: busca aulas com o instrutor (instructorId)
 */
export function useLessonHistory(otherUserId: string) {
    const { user } = useAuthStore();
    const isInstructor = user?.user_type === 'instructor';

    return useQuery({
        queryKey: ['lesson-history', otherUserId, user?.id],
        queryFn: () => {
            if (isInstructor) {
                // Instrutor vendo aulas de um aluno
                return getStudentLessons(otherUserId);
            } else {
                // Aluno vendo aulas com um instrutor
                return getStudentLessonsWithInstructor(otherUserId);
            }
        },
        enabled: !!otherUserId && !!user,
    });
}
