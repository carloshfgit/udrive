/**
 * Instructor Profile Stack Navigator
 *
 * Navegação interna da feature de perfil do instrutor.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { InstructorProfileScreen } from '../screens/InstructorProfileScreen';
import { PersonalInfoScreen } from '../../profile/screens/PersonalInfoScreen';

// Tipos de rotas do perfil do instrutor
export type InstructorProfileStackParamList = {
    InstructorProfileMain: undefined;
    InstructorPersonalInfo: undefined;
    // Futuras sub-telas:
    // MyVehicle: undefined;
    // BankingDetails: undefined;
    // Settings: undefined;
};

const Stack = createNativeStackNavigator<InstructorProfileStackParamList>();

export function InstructorProfileStack() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen name="InstructorProfileMain" component={InstructorProfileScreen} />
            <Stack.Screen name="InstructorPersonalInfo" component={PersonalInfoScreen} />
        </Stack.Navigator>
    );
}
