/**
 * Instructor Chat Stack Navigator
 *
 * Navegação interna da feature de chat para instrutores.
 */

import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { InstructorChatListScreen } from '../../shared-features/chat/screens/InstructorChatListScreen';
import { ChatRoomScreen } from '../../shared-features/chat/screens/ChatRoomScreen';
import { StudentLessonHistoryScreen } from '../../shared-features/chat/screens/StudentLessonHistoryScreen';

// Tipos de rotas do chat do instrutor
export type InstructorChatStackParamList = {
    ChatList: undefined;
    ChatRoom: { otherUserId: string; otherUserName: string };
    StudentLessonHistory: { studentId: string; studentName: string };
};

const Stack = createNativeStackNavigator<InstructorChatStackParamList>();

// Note: This matches the directory structure we created or will create
// features/shared-features/chat/screens/...

export function InstructorChatStack() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen name="ChatList" component={InstructorChatListScreen} />
            <Stack.Screen name="ChatRoom" component={ChatRoomScreen} />
            <Stack.Screen name="StudentLessonHistory" component={StudentLessonHistoryScreen} />
        </Stack.Navigator>
    );
}
