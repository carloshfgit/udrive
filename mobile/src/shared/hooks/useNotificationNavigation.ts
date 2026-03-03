/**
 * useNotificationNavigation Hook
 *
 * Resolve o deep linking de notificações: dado um action_type e action_id,
 * navega para a tela correspondente no app.
 */

import { useNavigation, CommonActions } from '@react-navigation/native';
import { useAuthStore } from '../../lib/store';
import { getScheduling as getInstructorBooking } from '../../features/instructor-app/api/scheduleApi';

interface NotificationData {
    type: string;
    action_type: 'SCHEDULING' | 'CHAT' | 'REVIEW' | 'PAYMENT';
    action_id: string;
}

/**
 * Hook para navegar ao clicar em uma notificação.
 *
 * Mapeia o `action_type` da notificação para a tela de destino:
 * - SCHEDULING → Detalhes do agendamento (aluno) ou Agenda na data (instrutor)
 * - CHAT → ChatRoom correspondente
 * - REVIEW → Detalhes da aula (para avaliar)
 * - PAYMENT → Detalhes do agendamento
 */
export function useNotificationNavigation() {
    const navigation = useNavigation<any>();
    const { user } = useAuthStore();

    async function handleNotificationPress(data: NotificationData) {
        console.log('[Notification] Navegando para:', data.action_type, data.action_id);

        const isInstructor = user?.user_type === 'instructor';

        switch (data.action_type) {
            case 'SCHEDULING':
            case 'PAYMENT':
                if (isInstructor) {
                    try {
                        // Para o instrutor, precisamos da data para abrir o calendário no dia correto
                        const booking = await getInstructorBooking(data.action_id);

                        // Se for uma notificação de reagendamento e ainda estiver pendente, vai para a tela de detalhes do reagendamento
                        if (
                            (data.type === 'RESCHEDULE_REQUESTED' || data.type === 'RESCHEDULE_RESPONDED') &&
                            booking.status.toLowerCase() === 'reschedule_requested'
                        ) {
                            navigation.navigate('Main', {
                                screen: 'InstructorSchedule',
                                params: {
                                    screen: 'RescheduleDetails',
                                    params: { scheduling: booking }
                                }
                            });
                            return;
                        }

                        const dateOnly = booking.scheduled_datetime.split('T')[0];

                        navigation.navigate('Main', {
                            screen: 'InstructorSchedule',
                            params: {
                                screen: 'InstructorScheduleMain',
                                params: { initialDate: dateOnly }
                            }
                        });
                    } catch (error) {
                        console.error('[Notification] Erro ao buscar detalhes para navegação:', error);
                        // Fallback para a agenda principal se falhar
                        navigation.navigate('Main', {
                            screen: 'InstructorSchedule'
                        });
                    }
                } else {
                    // Para o aluno, vamos direto para os detalhes
                    navigation.navigate('Main', {
                        screen: 'Scheduling',
                        params: {
                            screen: 'LessonDetails',
                            params: { schedulingId: data.action_id },
                        }
                    });
                }
                break;

            case 'CHAT':
                if (isInstructor) {
                    navigation.navigate('Main', {
                        screen: 'InstructorChat',
                        params: {
                            screen: 'ChatRoom',
                            params: { otherUserId: data.action_id },
                        }
                    });
                } else {
                    navigation.navigate('Main', {
                        screen: 'Scheduling',
                        params: {
                            screen: 'ChatRoom',
                            params: { otherUserId: data.action_id },
                        }
                    });
                }
                break;

            case 'REVIEW':
                // Reviews são tratados na tela de detalhes da aula no app do aluno
                navigation.navigate('Main', {
                    screen: 'Scheduling',
                    params: {
                        screen: 'LessonDetails',
                        params: { schedulingId: data.action_id },
                    }
                });
                break;

            default:
                console.warn('[Notification] action_type desconhecido:', data.action_type);
        }
    }

    return { handleNotificationPress };
}
