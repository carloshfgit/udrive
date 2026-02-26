"""
VehicleOwnership Enum

Enum para tipo de propriedade do veículo na aula.
"""

from enum import Enum


class VehicleOwnership(str, Enum):
    """
    Indica de quem é o veículo utilizado na aula.

    Valores:
        INSTRUCTOR: Veículo do instrutor.
        STUDENT: Veículo do aluno.
    """

    INSTRUCTOR = "instructor"
    STUDENT = "student"
