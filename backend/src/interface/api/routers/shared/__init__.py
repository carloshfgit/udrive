"""
Shared Routers

Routers compartilhados entre alunos e instrutores.
"""

from fastapi import APIRouter

from src.interface.api.routers.shared import instructors, payments

router = APIRouter()

# Incluir sub-routers
router.include_router(payments.router)
router.include_router(instructors.router)

__all__ = ["router"]
