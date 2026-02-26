"""
LessonCategory Enum

Enum para categorias de aula (CNH).
"""

from enum import Enum


class LessonCategory(str, Enum):
    """
    Categorias de CNH disponíveis para aulas.

    Valores:
        A: Categoria A (Moto).
        B: Categoria B (Carro).
        AB: Categoria AB (Moto e Carro).
    """

    A = "A"
    B = "B"
    AB = "AB"
