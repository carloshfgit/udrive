# Common Use Cases

## Overview
These use cases are shared across the system or apply to the generic `User` entity, regardless of whether they are a Student or Instructor. This includes authentication and basic account management.

## Use Cases
- **login_user.py**: Handles user authentication and token generation.
- **register_user.py**: Manages new user registration (creation of User, Student, or Instructor entities).
- **refresh_token.py**: Logic for refreshing access tokens using refresh tokens.
- **logout_user.py**: Handles secure logout (token invalidation).
- **reset_password.py**: Business logic for the password reset flow.

## Dependencies
Primarily depends on `IUserRepository`, `IAuthService` (for password hashing/validation), and `ITokenRepository`.
