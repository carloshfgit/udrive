"""
Instructor Routers

Routers exclusivos para instrutores.
"""

from fastapi import APIRouter

from src.interface.api.routers.instructor import (
    availability,
    earnings,
    profile,
    schedule,
    students,
)

router = APIRouter()

# Incluir sub-routers
router.include_router(profile.router)
router.include_router(availability.router)
router.include_router(schedule.router)
router.include_router(earnings.router)
router.include_router(students.router)

__all__ = ["router"]
