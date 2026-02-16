"""
Shared Routers

Routers compartilhados entre alunos e instrutores.
"""

from fastapi import APIRouter

from src.interface.api.routers.shared import chat, instructors, payments, webhooks

router = APIRouter()

# Incluir sub-routers
router.include_router(payments.router)
router.include_router(instructors.router)
router.include_router(chat.router)
router.include_router(webhooks.router)

__all__ = ["router"]
