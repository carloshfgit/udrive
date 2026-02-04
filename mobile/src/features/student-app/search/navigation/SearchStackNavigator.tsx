/**
 * GoDrive Mobile - SearchStackNavigator
 *
 * Stack Navigator para a tab de busca, permitindo navegação
 * da lista de instrutores para o perfil individual e agendamento.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { InstructorSearchScreen } from '../screens/InstructorSearchScreen';
import { InstructorProfileScreen } from '../../instructor-view/screens/InstructorProfileScreen';

// Telas de agendamento
import {
    SelectDateTimeScreen,
    ConfirmBookingScreen,
    BookingSuccessScreen,
} from '../../../shared-features/scheduling/screens';
import { TimeSlot } from '../../../shared-features/scheduling/api/schedulingApi';

// Tipos de parâmetros das rotas
export type SearchStackParamList = {
    InstructorSearch: undefined;
    InstructorProfile: { instructorId: string };
    // Fluxo de agendamento
    SelectDateTime: {
        instructorId: string;
        instructorName: string;
        instructorAvatar?: string;
        hourlyRate: number;
        licenseCategory?: string;
        rating?: number;
    };
    ConfirmBooking: {
        instructorId: string;
        instructorName: string;
        instructorAvatar?: string;
        hourlyRate: number;
        licenseCategory?: string;
        selectedDate: string;
        selectedSlot: TimeSlot;
        durationMinutes: number;
    };
    BookingSuccess: {
        schedulingId: string;
        instructorName: string;
        scheduledDatetime: string;
    };
};

const Stack = createNativeStackNavigator<SearchStackParamList>();

export function SearchStackNavigator() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen
                name="InstructorSearch"
                component={InstructorSearchScreen}
            />
            <Stack.Screen
                name="InstructorProfile"
                component={InstructorProfileScreen}
            />
            {/* Fluxo de agendamento */}
            <Stack.Screen
                name="SelectDateTime"
                component={SelectDateTimeScreen}
            />
            <Stack.Screen
                name="ConfirmBooking"
                component={ConfirmBookingScreen}
            />
            <Stack.Screen
                name="BookingSuccess"
                component={BookingSuccessScreen}
            />
        </Stack.Navigator>
    );
}

