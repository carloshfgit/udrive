/**
 * Profile Stack Navigator
 *
 * Navegação interna da feature de perfil do aluno.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { ProfileScreen } from '../screens/ProfileScreen';
import { PersonalInfoScreen } from '../screens/PersonalInfoScreen';

// Tipos de rotas do perfil
export type ProfileStackParamList = {
    ProfileMain: undefined;
    PersonalInfo: undefined;
    // Futuras sub-telas:
    // MyBookings: undefined;
    // LessonHistory: undefined;
    // PaymentMethods: undefined;
    // Settings: undefined;
};

const Stack = createNativeStackNavigator<ProfileStackParamList>();

export function ProfileStackNavigator() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen name="ProfileMain" component={ProfileScreen} />
            <Stack.Screen name="PersonalInfo" component={PersonalInfoScreen} />
        </Stack.Navigator>
    );
}
