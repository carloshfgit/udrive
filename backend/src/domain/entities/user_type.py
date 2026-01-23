"""
User Type Enum

Define os tipos de usuário suportados pelo sistema.
"""

from enum import Enum


class UserType(str, Enum):
    """Tipos de usuário no sistema GoDrive."""

    STUDENT = "student"  # Aluno
    INSTRUCTOR = "instructor"  # Instrutor
    ADMIN = "admin"  # Administrador
