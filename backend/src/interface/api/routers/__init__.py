"""
Interface - API Routers

Routers FastAPI organizados por domínio e tipo de usuário.
"""

from src.interface.api.routers import auth, health, instructor, shared, student

__all__ = [
    "auth",
    "health",
    "student",
    "instructor",
    "shared",
]
