/**
 * Root Navigator
 *
 * Roteia o usuário autenticado para o TabNavigator correto
 * baseado no tipo de usuário (student ou instructor).
 */

import React from 'react';
import { useAuthStore } from '../lib/store';
import { useWebSocket } from '../shared/hooks/useWebSocket';
import { StudentTabNavigator } from '../features/student-app/navigation/StudentTabNavigator';
import { InstructorTabNavigator } from '../features/instructor-app/navigation/InstructorTabNavigator';

export function RootNavigator() {
    const { user } = useAuthStore();

    // Ativa conexão WebSocket globalmente quando autenticado
    useWebSocket();

    // Instrutor vai para InstructorTabNavigator
    if (user?.user_type === 'instructor') {
        return <InstructorTabNavigator />;
    }

    // Default: aluno (e admin por enquanto) vai para StudentTabNavigator
    return <StudentTabNavigator />;
}
