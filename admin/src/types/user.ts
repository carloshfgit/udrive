export type UserType = 'student' | 'instructor' | 'admin';

export interface UserAdminScheduling {
    id: string;
    scheduled_datetime: string;
    status: string;
    price: number;
    instructor_name?: string;
    student_name?: string;
}

export interface UserAdminProfile {
    // Campos de Instrutor
    bio?: string;
    vehicle_type?: string;
    license_category?: string;
    hourly_rate?: number;
    rating?: number;
    total_reviews?: number;

    // Campos de Aluno
    learning_stage?: string;
    license_category_goal?: string;
    total_lessons?: number;
}

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
    biological_sex?: string;
    created_at: string;
    updated_at: string;
    profile?: UserAdminProfile;
    recent_schedulings?: UserAdminScheduling[];
}

export interface AdminUserFilters {
    q?: string;
    user_type?: 'student' | 'instructor' | 'admin' | 'all';
    is_active?: boolean | string;
    page: number;
    size: number;
}
