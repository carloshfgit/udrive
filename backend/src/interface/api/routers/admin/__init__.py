"""
Admin Routers

Routers exclusivos para administradores.
"""

from fastapi import APIRouter

from src.interface.api.routers.admin import disputes

router = APIRouter()

# Incluir sub-routers
router.include_router(disputes.router)

__all__ = ["router"]
