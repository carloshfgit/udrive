"""
Profile Schemas

Esquemas Pydantic para validação de requests e responses de perfis.
"""

from datetime import date
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# === Request Schemas ===


class UpdateInstructorProfileRequest(BaseModel):
    """Schema para atualização de perfil de instrutor."""

    bio: str | None = Field(None, max_length=1000, description="Biografia do instrutor")
    vehicle_type: str | None = Field(None, max_length=100, description="Modelo do veículo")
    license_category: str | None = Field(None, max_length=10, description="Categoria da CNH")
    hourly_rate: Decimal | None = Field(None, ge=0, description="Valor da hora/aula")
    is_available: bool | None = Field(None, description="Disponibilidade para novas aulas")
    full_name: str | None = Field(None, min_length=2, description="Nome completo")
    phone: str | None = Field(None, max_length=20, description="Telefone de contato")
    cpf: str | None = Field(None, max_length=14, description="CPF")
    birth_date: date | None = Field(None, description="Data de nascimento")
    biological_sex: str | None = Field(None, max_length=10, description="Sexo biológico (male/female)")
    latitude: float | None = Field(None, ge=-90, le=90, description="Latitude da localização")
    longitude: float | None = Field(None, ge=-180, le=180, description="Longitude da localização")


class UpdateStudentProfileRequest(BaseModel):
    """Schema para atualização de perfil de aluno."""

    preferred_schedule: str | None = Field(None, max_length=255, description="Horário preferido")
    license_category_goal: str | None = Field(None, max_length=10, description="Categoria pretendida")
    learning_stage: str | None = Field(None, max_length=50, description="Estágio de aprendizado")
    notes: str | None = Field(None, max_length=1000, description="Observações gerais")
    phone: str | None = Field(None, max_length=20, description="Telefone de contato")
    cpf: str | None = Field(None, max_length=14, description="CPF do aluno")
    birth_date: date | None = Field(None, description="Data de nascimento")
    full_name: str | None = Field(None, min_length=2, description="Nome completo")


class UpdateLocationRequest(BaseModel):
    """Schema para atualização de localização."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")


class SearchInstructorsRequest(BaseModel):
    """Schema para busca de instrutores (Query params normalmente, mas útil para docs)."""
    # Nota: Em GET requests, esses campos virão de Query Params, 
    # mas mantemos o schema para referência ou POST searches.
    pass


# === Response Schemas ===


class LocationResponse(BaseModel):
    """Schema de resposta para localização."""

    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)


class InstructorProfileResponse(BaseModel):
    """Schema de resposta para perfil de instrutor."""

    id: UUID
    user_id: UUID
    bio: str
    vehicle_type: str
    license_category: str
    hourly_rate: Decimal
    rating: float
    total_reviews: int
    is_available: bool
    full_name: str | None = None
    phone: str | None = None
    cpf: str | None = None
    birth_date: date | None = None
    biological_sex: str | None = None
    location: LocationResponse | None = None
    distance_km: float | None = None

    model_config = ConfigDict(from_attributes=True)


class StudentProfileResponse(BaseModel):
    """Schema de resposta para perfil de aluno."""

    id: UUID
    user_id: UUID
    preferred_schedule: str
    license_category_goal: str
    learning_stage: str
    notes: str
    total_lessons: int
    full_name: str | None = None
    phone: str | None = None
    cpf: str | None = None
    birth_date: date | None = None

    model_config = ConfigDict(from_attributes=True)


class InstructorSearchResponse(BaseModel):
    """Schema de resposta para busca de instrutores."""

    instructors: list[InstructorProfileResponse]
    total_count: int
    radius_km: float
    center_latitude: float
    center_longitude: float

    model_config = ConfigDict(from_attributes=True)
