# Student App Feature

## Overview
This module contains all functionalities specific to the Student user type in the GoDrive application. It includes screens for searching instructors, booking lessons, and managing the student's profile and settings.

## Structure
- `screens/`: Contains the UI screens for the student flow (e.g., `HomeScreen`, `SearchScreen`, `BookingScreen`).
- `components/`: Reusable UI components specific to the student interface.
- `hooks/`: Custom React hooks for student-specific logic (e.g., fetching nearby instructors).
- `api/`: API integration functions for endpoints under `/api/v1/student`.
- `navigation/`: `StudentTabNavigator` which defines the main bottom tab navigation for students.

## Key Components
- **StudentTabNavigator**: Manages the main navigation tabs for the student.
- **SearchScreen**: Allows students to search and filter instructors.
- **MapScreen**: Displays instructors on a map.

## Data Flow
Data is fetched using TanStack Query (React Query) hooks located in the `hooks/` directory, which call functions from the `api/` directory. These functions communicate with the backend via Axios.
