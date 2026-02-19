import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { MyLessonsScreen } from '../../../shared-features/scheduling/screens/MyLessonsScreen';
import { HistoryScreen } from '../screens/HistoryScreen';
import { LessonDetailsScreen } from '../screens/LessonDetailsScreen';
import { InstructorProfileScreen } from '../../instructor-view/screens/InstructorProfileScreen';
import { ChatRoomScreen } from '../../../shared-features/chat/screens/ChatRoomScreen';
import { StudentLessonHistoryScreen } from '../../../shared-features/chat/screens/StudentLessonHistoryScreen';
import {
    SelectDateTimeScreen,
    ConfirmBookingScreen,
    BookingSuccessScreen,
    CartScreen,
} from '../../../shared-features/scheduling/screens';
import { TimeSlot } from '../../../shared-features/scheduling/api/schedulingApi';

export type SchedulingStackParamList = {
    MyLessons: undefined;
    Cart: undefined;
    History: undefined;
    LessonDetails: { schedulingId: string };
    InstructorProfile: { instructorId: string };
    ChatRoom: { otherUserId: string; otherUserName: string };
    StudentLessonHistory: { studentId: string; studentName: string };
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
        rating?: number;
    };
    BookingSuccess: {
        schedulingId: string;
        instructorName: string;
        scheduledDatetime: string;
        instructorId: string;
        instructorAvatar?: string;
        hourlyRate: number;
        licenseCategory?: string;
        rating?: number;
    };
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
            <Stack.Screen name="Cart" component={CartScreen} />
            <Stack.Screen name="History" component={HistoryScreen} />
            <Stack.Screen name="LessonDetails" component={LessonDetailsScreen} />
            <Stack.Screen name="InstructorProfile" component={InstructorProfileScreen} />
            <Stack.Screen name="ChatRoom" component={ChatRoomScreen} />
            <Stack.Screen name="StudentLessonHistory" component={StudentLessonHistoryScreen} />
            <Stack.Screen name="SelectDateTime" component={SelectDateTimeScreen} />
            <Stack.Screen name="ConfirmBooking" component={ConfirmBookingScreen} />
            <Stack.Screen name="BookingSuccess" component={BookingSuccessScreen} />
        </Stack.Navigator>
    );
}
