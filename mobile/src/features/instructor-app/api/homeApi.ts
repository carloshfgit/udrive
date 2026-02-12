/**
 * Instructor Home API
 * 
 * Funções auxiliares para consolidar dados da Home.
 */

import { getNextInstructorClass, getScheduleByDate, Scheduling } from './scheduleApi';

/**
 * Obtém a próxima aula confirmada do instrutor.
 */
export async function getNextClass(): Promise<Scheduling | null> {
    return getNextInstructorClass();
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
