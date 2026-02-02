"""
Student Routers

Routers exclusivos para alunos.
"""

from fastapi import APIRouter

from src.interface.api.routers.student import instructors, lessons, payments, profile

router = APIRouter()

# Incluir sub-routers
router.include_router(profile.router)
router.include_router(instructors.router)
router.include_router(lessons.router)
router.include_router(payments.router)

__all__ = ["router"]
