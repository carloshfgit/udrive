/**
 * Instructor Schedule Stack Navigator
 *
 * Stack Navigator para a seção de Agenda do instrutor.
 * Inclui a tela principal de agenda e a tela de configuração de disponibilidade.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { InstructorScheduleScreen, InstructorAvailabilityScreen } from '../screens';

export type InstructorScheduleStackParamList = {
    InstructorScheduleMain: undefined;
    InstructorAvailability: undefined;
};

const Stack = createNativeStackNavigator<InstructorScheduleStackParamList>();

export function InstructorScheduleStack() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen
                name="InstructorScheduleMain"
                component={InstructorScheduleScreen}
            />
            <Stack.Screen
                name="InstructorAvailability"
                component={InstructorAvailabilityScreen}
            />
        </Stack.Navigator>
    );
}
