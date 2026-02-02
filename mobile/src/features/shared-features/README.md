# Shared Features

## Overview
This module contains features that are common to both Student and Instructor users. These features maintain consistent logic and UI across different user types but may have slight variations in presentation.

## Structure
- `profile/`: Shared profile management components and logic (e.g., editing personal info, viewing profile).
- `scheduling/`: Core scheduling logic and UI components used by both parties to view appointment details.
- `chat/`: (Planned) Messaging system between students and instructors.

## Key Components
- **ProfileEditScreen**: A shared screen or component set for editing user details.
- **AppointmentCard**: A unified card component to display lesson details in lists.

## Data Flow
Shared features typically interface with `/api/v1/shared` endpoints or use conditional logic to call specific endpoints based on the current user type.
