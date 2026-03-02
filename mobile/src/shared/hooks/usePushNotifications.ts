/**
 * usePushNotifications Hook
 *
 * Gerencia o ciclo de vida das push notifications via Expo:
 * - Solicita permissões
 * - Registra o Expo Push Token no backend
 * - Configura handlers para notificações em foreground
 * - Escuta cliques em notificações para deep linking
 */

import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { useEffect, useRef } from 'react';
import { Platform } from 'react-native';
import { useAuthStore } from '@lib/index';
import { api, SHARED_API } from '@lib/axios';
import { useNotificationNavigation } from './useNotificationNavigation';
import { useNotificationStore } from '../../features/shared-features/notifications/stores/notificationStore';
import { useQueryClient } from '@tanstack/react-query';

// Configuração global: como a notificação é exibida quando o app está em foreground
Notifications.setNotificationHandler({
    handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
        shouldShowBanner: true,
        shouldShowList: true,
    }),
});

/**
 * Hook para gerenciar push notifications.
 *
 * Deve ser chamado uma vez no nível raiz da navegação (RootNavigator).
 * Registra o token automaticamente quando o usuário está autenticado
 * e limpa os listeners no unmount.
 */
export function usePushNotifications() {
    const { user } = useAuthStore();
    const { handleNotificationPress } = useNotificationNavigation();
    const incrementUnread = useNotificationStore((s) => s.incrementUnread);
    const queryClient = useQueryClient();
    const notificationListener = useRef<Notifications.EventSubscription>(undefined);
    const responseListener = useRef<Notifications.EventSubscription>(undefined);

    useEffect(() => {
        if (!user) return;

        registerForPushNotifications();

        // Listener: notificação recebida com app em foreground
        notificationListener.current =
            Notifications.addNotificationReceivedListener((notification) => {
                console.log('[Push] Notificação recebida em foreground:', notification.request.content.title);
                // Incrementar badge e invalidar cache
                incrementUnread();
                queryClient.invalidateQueries({ queryKey: ['notifications'] });
                queryClient.invalidateQueries({ queryKey: ['notifications-unread-count'] });
            });

        // Listener: usuário clicou na notificação (foreground ou background)
        responseListener.current =
            Notifications.addNotificationResponseReceivedListener((response) => {
                const data = response.notification.request.content.data as {
                    type?: string;
                    action_type?: string;
                    action_id?: string;
                };
                if (data.action_type && data.action_id) {
                    handleNotificationPress(data as any);
                }
            });

        return () => {
            notificationListener.current?.remove();
            responseListener.current?.remove();
        };
    }, [user]);

    /**
     * Solicita permissão e registra o push token no backend.
     */
    async function registerForPushNotifications() {
        // Push notifications não funcionam em emulador
        if (!Device.isDevice) {
            console.log('[Push] Push notifications requerem dispositivo físico');
            return;
        }

        // Solicitar permissão
        const { status: existingStatus } = await Notifications.getPermissionsAsync();
        let finalStatus = existingStatus;

        if (existingStatus !== 'granted') {
            const { status } = await Notifications.requestPermissionsAsync();
            finalStatus = status;
        }

        if (finalStatus !== 'granted') {
            console.log('[Push] Permissão negada pelo usuário');
            return;
        }

        // Obter Expo Push Token
        try {
            const projectId = Constants.expoConfig?.extra?.eas?.projectId;
            const tokenData = await Notifications.getExpoPushTokenAsync({
                projectId,
            });

            console.log('[Push] Token obtido:', tokenData.data.substring(0, 30) + '...');

            // Registrar token no backend
            await api.post(`${SHARED_API}/notifications/push-token`, {
                token: tokenData.data,
                platform: Platform.OS,
            });

            console.log('[Push] Token registrado no backend');
        } catch (error) {
            console.error('[Push] Erro ao registrar token:', error);
        }

        // Configurar canal de notificação no Android
        if (Platform.OS === 'android') {
            await Notifications.setNotificationChannelAsync('default', {
                name: 'Padrão',
                importance: Notifications.AndroidImportance.HIGH,
                vibrationPattern: [0, 250, 250, 250],
                lightColor: '#FF6B35',
            });
        }
    }
}
