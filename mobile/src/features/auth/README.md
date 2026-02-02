# Auth Feature

## Overview
This module handles the authentication flow for all users. It manages login, registration, password recovery, and token management (storage and rotation).

## Structure
- `screens/`: Login, Register, ForgotPassword screens.
- `services/`: Authentication service (AuthService) to handle token storage (SecureStore) and Axios interceptors.
- `hooks/`: `useAuth` hook providing the authentication context (user object, login/logout functions).
- `api/`: API calls to `/api/v1/auth`.

## Key Components
- **AuthProvider**: React Context provider that wraps the app and manages global auth state.
- **LoginScreen**: Entry point for user authentication.

## Data Flow
The `AuthProvider` initializes by checking storage for existing tokens. API calls for login/register return JWTs which are stored securely. The `useAuth` hook exposes this state to the rest of the app.
