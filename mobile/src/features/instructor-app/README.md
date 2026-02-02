# Instructor App Feature

## Overview
This module contains all functionalities specific to the Instructor user type in the GoDrive application. It handles the instructor's dashboard, schedule management, availability settings, and earnings view.

## Structure
- `screens/`: UI screens for the instructor flow (e.g., `DashboardScreen`, `ScheduleScreen`, `EarningsScreen`).
- `components/`: UI components specific to the instructor interface.
- `hooks/`: Custom hooks for instructor logic (e.g., managing availability).
- `api/`: API integration functions for endpoints under `/api/v1/instructor`.
- `navigation/`: `InstructorTabNavigator` which defines the main bottom tab navigation for instructors.

## Key Components
- **InstructorTabNavigator**: Manages the main navigation tabs for the instructor.
- **DashboardScreen**: High-level view of upcoming classes and stats.
- **ScheduleScreen**: Interface for managing calendar and availability.

## Data Flow
Uses TanStack Query to manage server state. specific hooks in `hooks/` wrap API calls defined in `api/`.
