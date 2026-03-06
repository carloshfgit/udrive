"""
Admin Routers

Routers exclusivos para administradores.
"""

from fastapi import APIRouter

from src.interface.api.routers.admin import disputes, users, schedulings

router = APIRouter()

# Incluir sub-routers
router.include_router(disputes.router)
router.include_router(users.router)
router.include_router(schedulings.router)

__all__ = ["router"]
