"""
Interface - API Routers

Routers FastAPI organizados por domínio.
"""

from src.interface.api.routers import auth, health, instructors, payments, schedulings, students

__all__ = [
    "auth",
    "health",
    "instructors",
    "students",
    "schedulings",
    "payments",
]
