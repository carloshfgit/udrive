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
    LessonOptionsScreen,
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
    LessonOptions: {
        instructorId: string;
        instructorName: string;
        instructorAvatar?: string;
        licenseCategory: string;
        rating?: number;
        priceAInstructor?: number | null;
        priceAStudent?: number | null;
        priceBInstructor?: number | null;
        priceBStudent?: number | null;
    };
    SelectDateTime: {
        instructorId: string;
        instructorName: string;
        instructorAvatar?: string;
        selectedPrice: number;
        licenseCategory?: string;
        rating?: number;
        lessonCategory: string;
        vehicleOwnership: string;
    };
    ConfirmBooking: {
        instructorId: string;
        instructorName: string;
        instructorAvatar?: string;
        selectedPrice: number;
        licenseCategory?: string;
        selectedDate: string;
        selectedSlot: TimeSlot;
        durationMinutes: number;
        rating?: number;
        lessonCategory: string;
        vehicleOwnership: string;
    };
    BookingSuccess: {
        schedulingId: string;
        instructorName: string;
        scheduledDatetime: string;
        instructorId: string;
        instructorAvatar?: string;
        selectedPrice: number;
        licenseCategory?: string;
        rating?: number;
        lessonCategory: string;
        vehicleOwnership: string;
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
                name="LessonOptions"
                component={LessonOptionsScreen}
            />
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

