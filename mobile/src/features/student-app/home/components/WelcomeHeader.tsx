import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Bell } from 'lucide-react-native';
import { Avatar } from '../../../../shared/components/Avatar';

interface WelcomeHeaderProps {
    name?: string;
    avatarUrl?: string;
    onPressNotifications?: () => void;
    notificationCount?: number;
}

export function WelcomeHeader({
    name = 'Aluno',
    avatarUrl,
    onPressNotifications,
    notificationCount = 0
}: WelcomeHeaderProps) {
    return (
        <View className="flex-row items-center justify-between px-6 py-4 bg-white">
            <View className="flex-row items-center">
                <Avatar
                    fallback={name}
                    source={avatarUrl}
                    size="md"
                    className="border-2 border-primary-50"
                />
                <View className="ml-4">
                    <Text className="text-neutral-500 text-xs font-medium uppercase tracking-wider">
                        Bem-vindo(a) de volta!
                    </Text>
                    <Text className="text-neutral-900 text-xl font-black">
                        Olá, {name.split(' ')[0]} 👋
                    </Text>
                </View>
            </View>

            <TouchableOpacity
                onPress={onPressNotifications}
                className="w-12 h-12 items-center justify-center bg-neutral-50 rounded-2xl relative"
                activeOpacity={0.7}
            >
                <Bell size={24} color="#171717" />
                {notificationCount > 0 && (
                    <View className="absolute top-3 right-3 w-4 h-4 bg-red-500 rounded-full border-2 border-white items-center justify-center">
                        <Text className="text-white text-[8px] font-bold">
                            {notificationCount > 9 ? '9+' : notificationCount}
                        </Text>
                    </View>
                )}
            </TouchableOpacity>
        </View>
    );
}
