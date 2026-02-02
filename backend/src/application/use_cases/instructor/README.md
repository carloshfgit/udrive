# Instructor Use Cases

## Overview
This directory maps the business capabilities of the Instructor domain. It includes logic for profile management, availability settings, and location updates specific to instructors.

## Use Cases
- **update_instructor_profile.py**: Handles updates to instructor-specific fields (e.g., vehicle info, bio).
- **update_instructor_location.py**: Processes real-time or periodic location updates for the instructor, essential for the "nearby instructors" feature.

## Dependencies
Relies heavily on `IInstructorRepository` and potentially `ILocationService` for handling geospatial data updates.
