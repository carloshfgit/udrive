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
import { View } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../lib/store';
import { useWebSocket } from '../shared/hooks/useWebSocket';
import { usePushNotifications } from '../shared/hooks/usePushNotifications';
import { useInAppBanners } from '../shared/hooks/useInAppBanners';
import { StudentTabNavigator } from '../features/student-app/navigation/StudentTabNavigator';
import { InstructorTabNavigator } from '../features/instructor-app/navigation/InstructorTabNavigator';
import { PaymentResultScreen } from '../screens/PaymentResultScreen';
import { NotificationsScreen } from '../features/shared-features/notifications/screens/NotificationsScreen';
import { InAppBanner } from '../shared/components/InAppBanner';

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

    // Ativa banners de notificação in-app (escuta eventos NOTIFICATION via WS)
    useInAppBanners();

    return (
        <View style={{ flex: 1 }}>
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

            {/* Banner de notificação in-app — renderizado sobre toda a navegação */}
            <InAppBanner />
        </View>
    );
}

