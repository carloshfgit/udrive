/**
 * useNotificationNavigation Hook
 *
 * Resolve o deep linking de notificações: dado um action_type e action_id,
 * navega para a tela correspondente no app.
 */

import { useNavigation, CommonActions } from '@react-navigation/native';

interface NotificationData {
    type: string;
    action_type: 'SCHEDULING' | 'CHAT' | 'REVIEW' | 'PAYMENT';
    action_id: string;
}

/**
 * Hook para navegar ao clicar em uma notificação.
 *
 * Mapeia o `action_type` da notificação para a tela de destino:
 * - SCHEDULING → ScheduleDetails
 * - CHAT → ChatScreen
 * - REVIEW → ReviewScreen
 * - PAYMENT → ScheduleDetails
 */
export function useNotificationNavigation() {
    const navigation = useNavigation();

    function handleNotificationPress(data: NotificationData) {
        console.log('[Notification] Navegando para:', data.action_type, data.action_id);

        switch (data.action_type) {
            case 'SCHEDULING':
                navigation.dispatch(
                    CommonActions.navigate({
                        name: 'ScheduleDetails',
                        params: { schedulingId: data.action_id },
                    })
                );
                break;

            case 'CHAT':
                navigation.dispatch(
                    CommonActions.navigate({
                        name: 'ChatScreen',
                        params: { otherUserId: data.action_id },
                    })
                );
                break;

            case 'REVIEW':
                navigation.dispatch(
                    CommonActions.navigate({
                        name: 'ReviewScreen',
                        params: { schedulingId: data.action_id },
                    })
                );
                break;

            case 'PAYMENT':
                navigation.dispatch(
                    CommonActions.navigate({
                        name: 'ScheduleDetails',
                        params: { schedulingId: data.action_id },
                    })
                );
                break;

            default:
                console.warn('[Notification] action_type desconhecido:', data.action_type);
        }
    }

    return { handleNotificationPress };
}
