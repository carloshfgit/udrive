import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Home, Search, BookOpen, Calendar, User } from 'lucide-react-native';

import { HomeScreen } from '../features/home/screens/HomeScreen';
import { InstructorSearchScreen } from '../features/search/screens/InstructorSearchScreen';
import { LearningCenterScreen } from '../features/learning/screens/LearningCenterScreen';
import { MyLessonsScreen } from '../features/scheduling/screens/MyLessonsScreen';
import { ProfileScreen } from '../features/profile/screens/ProfileScreen';

const Tab = createBottomTabNavigator();

export function StudentTabNavigator() {
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
                name="Home"
                component={HomeScreen}
                options={{
                    tabBarLabel: 'Início',
                    tabBarIcon: ({ color, size }) => <Home color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="Search"
                component={InstructorSearchScreen}
                options={{
                    tabBarLabel: 'Buscar',
                    tabBarIcon: ({ color, size }) => <Search color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="Learning"
                component={LearningCenterScreen}
                options={{
                    tabBarLabel: 'Aprender',
                    tabBarIcon: ({ color, size }) => <BookOpen color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="Scheduling"
                component={MyLessonsScreen}
                options={{
                    tabBarLabel: 'Aulas',
                    tabBarIcon: ({ color, size }) => <Calendar color={color} size={size} />,
                }}
            />
            <Tab.Screen
                name="Profile"
                component={ProfileScreen}
                options={{
                    tabBarLabel: 'Perfil',
                    tabBarIcon: ({ color, size }) => <User color={color} size={size} />,
                }}
            />
        </Tab.Navigator>
    );
}
