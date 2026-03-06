import { User } from './user';

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: User;
}

export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}
