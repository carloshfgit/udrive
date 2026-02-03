/**
 * GoDrive Mobile - SearchStackNavigator
 *
 * Stack Navigator para a tab de busca, permitindo navegação
 * da lista de instrutores para o perfil individual.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { InstructorSearchScreen } from '../screens/InstructorSearchScreen';
import { InstructorProfileScreen } from '../../instructor-view/screens/InstructorProfileScreen';

// Tipos de parâmetros das rotas
export type SearchStackParamList = {
    InstructorSearch: undefined;
    InstructorProfile: { instructorId: string };
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
        </Stack.Navigator>
    );
}
