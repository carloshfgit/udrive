/**
 * Root Navigator
 *
 * Roteia o usuário autenticado para o TabNavigator correto
 * baseado no tipo de usuário (student ou instructor).
 * 
 * Usa um Stack Navigator para permitir telas modais como
 * PaymentResult (acessada via deep link após checkout).
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../lib/store';
import { useWebSocket } from '../shared/hooks/useWebSocket';
import { usePushNotifications } from '../shared/hooks/usePushNotifications';
import { StudentTabNavigator } from '../features/student-app/navigation/StudentTabNavigator';
import { InstructorTabNavigator } from '../features/instructor-app/navigation/InstructorTabNavigator';
import { PaymentResultScreen } from '../screens/PaymentResultScreen';
import { NotificationsScreen } from '../features/shared-features/notifications/screens/NotificationsScreen';

const Stack = createNativeStackNavigator();

function MainNavigator() {
    const { user } = useAuthStore();

    if (user?.user_type === 'instructor') {
        return <InstructorTabNavigator />;
    }

    return <StudentTabNavigator />;
}

export function RootNavigator() {
    // Ativa conexão WebSocket globalmente quando autenticado
    useWebSocket();

    // Ativa push notifications (registro de token e listeners)
    usePushNotifications();

    return (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
            <Stack.Screen name="Main" component={MainNavigator} />
            <Stack.Screen
                name="PaymentResult"
                component={PaymentResultScreen}
                options={{
                    presentation: 'modal',
                    animation: 'slide_from_bottom',
                }}
            />
            <Stack.Screen
                name="Notifications"
                component={NotificationsScreen}
                options={{
                    presentation: 'modal',
                    animation: 'slide_from_bottom',
                }}
            />
        </Stack.Navigator>
    );
}

