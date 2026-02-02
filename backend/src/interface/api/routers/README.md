# API Routers

## Overview
This directory contains the FastAPI routers that define the HTTP interface of the application. The routers are organized by implementation scope (Standard/Instructor/Shared) to align with the frontend structure and security requirements.

## Structure
- `student/`: Endpoints prefixed with `/api/v1/student`. protected by `require_student` dependency.
- `instructor/`: Endpoints prefixed with `/api/v1/instructor`. protected by `require_instructor` dependency.
- `shared/`: Endpoints prefixed with `/api/v1/shared`. accessible to authenticated users (both types).
- `auth.py`: Authentication endpoints (login, register) - Public access.
- `health.py`: Health check endpoint for monitoring/deployment.

## Dependencies
Routers interface with the Application Layer (Use Cases) via `dependencies.py`, which injects necessary services and repositories. logic should be kept minimal here, delegating to Use Cases.
