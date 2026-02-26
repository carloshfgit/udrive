/**
 * Instructor Profile Stack Navigator
 *
 * Navegação interna da feature de perfil do instrutor.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { InstructorProfileScreen } from '../screens/InstructorProfileScreen';
import { EditInstructorProfileScreen } from '../screens/EditInstructorProfileScreen';
import { EditPublicProfileScreen } from '../screens/EditPublicProfileScreen';
import { LinkMercadoPagoScreen } from '../screens/LinkMercadoPagoScreen';
import { InstructorReviewsScreen } from '../screens/InstructorReviewsScreen';

// Tipos de rotas do perfil do perfil do instrutor
export type InstructorProfileStackParamList = {
    InstructorProfileMain: undefined;
    EditInstructorProfile: undefined;
    EditPublicProfile: undefined;
    LinkMercadoPago: undefined;
    InstructorReviews: undefined;
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
            <Stack.Screen name="EditInstructorProfile" component={EditInstructorProfileScreen} />
            <Stack.Screen name="EditPublicProfile" component={EditPublicProfileScreen} />
            <Stack.Screen name="LinkMercadoPago" component={LinkMercadoPagoScreen} />
            <Stack.Screen name="InstructorReviews" component={InstructorReviewsScreen} />
        </Stack.Navigator>
    );
}
