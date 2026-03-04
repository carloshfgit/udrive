/**
 * Instructor Settings Store
 * 
 * Gerencia configurações locais do instrutor, como a meta mensal.
 * Usa expo-secure-store para persistência simplificada.
 */

import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

const MONTHLY_GOAL_KEY = 'godrive_instructor_monthly_goal';

interface InstructorSettingsState {
    monthlyGoal: number;
    isLoading: boolean;
}

interface InstructorSettingsActions {
    setMonthlyGoal: (goal: number) => Promise<void>;
    loadSettings: () => Promise<void>;
}

export const useInstructorSettingsStore = create<InstructorSettingsState & InstructorSettingsActions>((set) => ({
    // Estado inicial
    monthlyGoal: 0,
    isLoading: true,

    // Ações
    setMonthlyGoal: async (goal) => {
        try {
            await SecureStore.setItemAsync(MONTHLY_GOAL_KEY, goal.toString());
            set({ monthlyGoal: goal });
        } catch (error) {
            console.error('[InstructorSettingsStore] Erro ao salvar meta:', error);
        }
    },

    loadSettings: async () => {
        set({ isLoading: true });
        try {
            const savedGoal = await SecureStore.getItemAsync(MONTHLY_GOAL_KEY);
            if (savedGoal) {
                set({ monthlyGoal: Number(savedGoal), isLoading: false });
            } else {
                set({ isLoading: false });
            }
        } catch (error) {
            console.error('[InstructorSettingsStore] Erro ao carregar configurações:', error);
            set({ isLoading: false });
        }
    },
}));
