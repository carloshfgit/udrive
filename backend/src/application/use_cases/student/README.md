# Student Use Cases

## Overview
This directory contains the business logic strictly related to the Student domain. These use cases encapsulate specific operations that a student can perform or that are performed on a student entity.

## Use Cases
- **search_instructors_by_location.py**: Logic to find instructors within a certain radius of a given coordinate.
- **get_nearby_instructors.py**: Similar to search, retrieves instructors near a location (potentially overlapping logic to be consolidated).
- **update_student_profile.py**: specific business rules for updating a student's profile information.

## Dependencies
These use cases typically depend on `IStudentRepository`, `IInstructorRepository`, and `ILocationService` (for geospatial queries).
