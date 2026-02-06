import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MyLessonsScreen } from '../../../shared-features/scheduling/screens/MyLessonsScreen';
import { HistoryScreen } from '../screens/HistoryScreen';

export type SchedulingStackParamList = {
    MyLessons: undefined;
    History: undefined;
};

const Stack = createNativeStackNavigator<SchedulingStackParamList>();

export function SchedulingStackNavigator() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen name="MyLessons" component={MyLessonsScreen} />
            <Stack.Screen name="History" component={HistoryScreen} />
        </Stack.Navigator>
    );
}
