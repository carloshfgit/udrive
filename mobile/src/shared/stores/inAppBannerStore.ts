/**
 * In-App Banner Store (Zustand)
 *
 * Gerencia a fila de banners de notificação in-app.
 * Garante que apenas um banner seja exibido por vez,
 * promovendo o próximo da fila automaticamente ao dismiss.
 *
 * A flag `isChatScreenActive` é usada para suprimir
 * banners de mensagem quando o ChatRoomScreen está aberto.
 */

import { create } from 'zustand';

// === Tipos ===

export type InAppBannerType = 'scheduling' | 'chat' | 'reschedule' | 'info';

export interface InAppBanner {
    /** ID único do banner (gerado no momento do enqueue) */
    id: string;
    /** Título exibido no banner */
    title: string;
    /** Corpo/descrição curta */
    body: string;
    /** Tipo visual do banner (define ícone e cor) */
    type: InAppBannerType;
    /** Tipo de ação para deep linking (SCHEDULING, CHAT, etc.) */
    actionType?: 'SCHEDULING' | 'CHAT' | 'REVIEW' | 'PAYMENT';
    /** ID do recurso de destino para navegação */
    actionId?: string;
    /** Tipo original da notificação do backend (ex: 'NEW_SCHEDULING') */
    notificationType?: string;
}

interface InAppBannerState {
    /** Fila de banners pendentes (FIFO) */
    queue: InAppBanner[];
    /** Banner atualmente visível */
    currentBanner: InAppBanner | null;
    /** Flag: ChatRoomScreen está ativo (suprime banners de chat) */
    isChatScreenActive: boolean;
}

interface InAppBannerActions {
    /** Adiciona um banner à fila. Se nenhum está visível, exibe imediatamente. */
    enqueue: (banner: Omit<InAppBanner, 'id'>) => void;
    /** Descarta o banner atual e promove o próximo da fila. */
    dismiss: () => void;
    /** Define se o ChatRoomScreen está ativo (para supressão). */
    setChatScreenActive: (active: boolean) => void;
}

// Gera IDs únicos simples (sem dependência externa)
let bannerId = 0;
const generateId = (): string => `banner_${Date.now()}_${++bannerId}`;

export const useInAppBannerStore = create<InAppBannerState & InAppBannerActions>(
    (set, get) => ({
        queue: [],
        currentBanner: null,
        isChatScreenActive: false,

        enqueue: (bannerData) => {
            const state = get();

            // Suprimir banners de chat se o ChatRoomScreen está aberto
            if (bannerData.type === 'chat' && state.isChatScreenActive) {
                return;
            }

            const banner: InAppBanner = {
                ...bannerData,
                id: generateId(),
            };

            if (!state.currentBanner) {
                // Nenhum banner ativo — exibir imediatamente
                set({ currentBanner: banner });
            } else {
                // Já tem banner ativo — enfileirar
                set({ queue: [...state.queue, banner] });
            }
        },

        dismiss: () => {
            const state = get();
            const [next, ...rest] = state.queue;

            set({
                currentBanner: next ?? null,
                queue: rest,
            });
        },

        setChatScreenActive: (active) => {
            set({ isChatScreenActive: active });
        },
    })
);
