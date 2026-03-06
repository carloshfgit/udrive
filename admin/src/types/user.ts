export type UserType = 'student' | 'instructor' | 'admin';

export interface User {
    id: string;
    email: string;
    full_name: string;
    user_type: UserType;
    is_active: boolean;
    is_verified: boolean;
    phone?: string;
    cpf?: string;
    birth_date?: string;
    created_at: string;
    updated_at: string;
}
