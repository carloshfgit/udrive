/**
 * Instructor Tab Navigator
 *
 * Bottom Tab Navigator para a experiência do instrutor com 4 abas:
 * 1. Início/Feed
 * 2. Agenda
 * 3. Dashboard
 * 4. Perfil
 */

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Home, Calendar, BarChart2, User } from 'lucide-react-native';

import {
    InstructorHomeScreen,
    InstructorScheduleScreen,
    InstructorDashboardScreen,
} from '../features/instructor-app/screens';
import { InstructorProfileStack } from '../features/instructor-app/navigation/InstructorProfileStack';

const Tab = createBottomTabNavigator();

export function InstructorTabNavigator() {
    return (
        <Tab.Navigator
            screenOptions={{
                headerShown: false,
                tabBarActiveTintColor: '#2563EB', // blue-600
                tabBarInactiveTintColor: '#6B7280', // gray-500
                tabBarStyle: {
                    borderTopColor: '#E5E7EB', // gray-200
                    paddingTop: 8,
                    paddingBottom: 8,
                    height: 60,
                },
                tabBarLabelStyle: {
                    fontSize: 12,
                    fontWeight: '500',
                    marginBottom: 4,
                },
            }}
        >
            <Tab.Screen
                name="InstructorHome"
                component={InstructorHomeScreen}
                options={{
                    tabBarLabel: 'Início',
                    tabBarIcon: ({ color, size }) => <Home color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="InstructorSchedule"
                component={InstructorScheduleScreen}
                options={{
                    tabBarLabel: 'Agenda',
                    tabBarIcon: ({ color, size }) => <Calendar color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="InstructorDashboard"
                component={InstructorDashboardScreen}
                options={{
                    tabBarLabel: 'Dashboard',
                    tabBarIcon: ({ color, size }) => <BarChart2 color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="InstructorProfile"
                component={InstructorProfileStack}
                options={{
                    tabBarLabel: 'Perfil',
                    tabBarIcon: ({ color, size }) => <User color={color} size={size} />,
                }}
            />
        </Tab.Navigator>
    );
}
