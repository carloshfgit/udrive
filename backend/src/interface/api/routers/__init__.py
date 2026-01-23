"""
Interface - API Routers

Routers FastAPI organizados por domínio.
"""

from src.interface.api.routers import auth, health

__all__ = ["auth", "health"]
