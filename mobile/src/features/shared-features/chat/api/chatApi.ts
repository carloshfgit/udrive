/**
 * GoDrive Mobile - Chat API
 *
 * Funções para consumir os endpoints de chat e mensagens.
 */

import api, { SHARED_API, INSTRUCTOR_API } from '../../../../lib/axios';
import { BookingResponse } from '../../scheduling/api/schedulingApi';

// === Tipos ===

export interface MessageResponse {
    id: string;
    sender_id: string;
    receiver_id: string;
    content: string;
    timestamp: string;
    is_read: boolean;
}

export interface ConversationResponse {
    student_id: string;
    student_name: string;
    last_message: MessageResponse | null;
    unread_count: number;
    next_lesson_at: string | null;
}

export interface SendMessageRequest {
    receiver_id: string;
    content: string;
}

// === Funções de API ===

/**
 * Envia uma nova mensagem.
 */
export async function sendMessage(data: SendMessageRequest): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(
        `${SHARED_API}/chat/messages`,
        data
    );
    return response.data;
}

/**
 * Lista as conversas ativas do usuário logado.
 */
export async function getConversations(): Promise<ConversationResponse[]> {
    const response = await api.get<ConversationResponse[]>(
        `${SHARED_API}/chat/conversations`
    );
    return response.data;
}

/**
 * Lista o histórico de mensagens com um usuário específico.
 */
export async function getMessages(otherUserId: string): Promise<MessageResponse[]> {
    const response = await api.get<MessageResponse[]>(
        `${SHARED_API}/chat/messages/${otherUserId}`
    );
    return response.data;
}

/**
 * Busca o histórico de aulas de um aluno específico (usado pelo instrutor).
 */
export async function getStudentLessons(studentId: string): Promise<BookingResponse[]> {
    const response = await api.get<BookingResponse[]>(
        `${INSTRUCTOR_API}/students/${studentId}/lessons`
    );
    return response.data;
}
