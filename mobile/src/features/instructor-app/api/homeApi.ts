/**
 * Instructor Home API
 * 
 * Funções auxiliares para consolidar dados da Home.
 */

import { getInstructorSchedule, getScheduleByDate, Scheduling } from './scheduleApi';

/**
 * Obtém a próxima aula confirmada do instrutor.
 */
export async function getNextClass(): Promise<Scheduling | null> {
    const response = await getInstructorSchedule({
        status_filter: 'confirmed',
        limit: 10, // Buscamos algumas para filtrar as que já passaram se necessário
    });

    const now = new Date();

    // Filtrar aulas que ainda não aconteceram e ordenar por data ASC
    const upcoming = response.schedulings
        .map(s => ({ ...s, date: new Date(s.scheduled_datetime) }))
        .filter(s => s.date > now)
        .sort((a, b) => a.date.getTime() - b.date.getTime());

    return upcoming.length > 0 ? upcoming[0] : null;
}

/**
 * Obtém o resumo de ganhos do dia atual.
 */
export async function getDailySummary(): Promise<{ total: number; count: number }> {
    const today = new Date().toISOString().split('T')[0];
    const response = await getScheduleByDate(today);

    const completed = response.schedulings.filter(s => s.status === 'completed');

    const total = completed.reduce((sum, s) => sum + Number(s.price), 0);

    return {
        total,
        count: completed.length
    };
}
