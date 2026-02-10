"""
InstructorProfile SQLAlchemy Model

Modelo de banco de dados para perfis de instrutores com suporte a PostGIS.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.entities.instructor_profile import InstructorProfile
from src.domain.entities.location import Location
from src.infrastructure.db.database import Base


class InstructorProfileModel(Base):
    """
    Modelo SQLAlchemy para tabela de perfis de instrutores.

    Utiliza PostGIS para armazenamento e queries espaciais.
    """

    __tablename__ = "instructor_profiles"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Key para User
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Informações do perfil
    bio: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )
    vehicle_type: Mapped[str] = mapped_column(
        String(100),
        default="",
        nullable=False,
    )
    license_category: Mapped[str] = mapped_column(
        String(10),
        default="B",
        nullable=False,
    )
    hourly_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("80.00"),
        nullable=False,
    )

    # Avaliações
    rating: Mapped[float] = mapped_column(
        Numeric(3, 2),
        default=0.0,
        nullable=False,
    )
    total_reviews: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    # Disponibilidade
    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # Localização (PostGIS Point, SRID 4326 = WGS84)
    location: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
    )

    # Cidade (obtida via geocodificação reversa)
    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # Relacionamentos
    user = relationship("UserModel", back_populates="instructor_profile")

    # Índices
    __table_args__ = (
        # Índice GIST para busca espacial
        Index("ix_instructor_profiles_location", "location", postgresql_using="gist"),
        # Índice composto para filtrar por disponibilidade
        Index("ix_instructor_profiles_available_rating", "is_available", "rating"),
    )

    def to_entity(self) -> InstructorProfile:
        """Converte o modelo para entidade de domínio."""
        # Converter geometria PostGIS para Location
        location_entity = None
        if self.location is not None:
            # A geometria é retornada como WKB, precisamos converter
            # Isso será feito na query com ST_AsText
            pass  # Tratado na query do repositório

        return InstructorProfile(
            id=self.id,
            user_id=self.user_id,
            bio=self.bio,
            city=self.city,
            vehicle_type=self.vehicle_type,
            license_category=self.license_category,
            hourly_rate=self.hourly_rate,
            location=location_entity,
            rating=float(self.rating),
            total_reviews=self.total_reviews,
            is_available=self.is_available,
            full_name=self.user.full_name if "user" in self.__dict__ and self.user else None,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, profile: InstructorProfile) -> "InstructorProfileModel":
        """Cria modelo a partir de entidade de domínio."""
        location_wkt = None
        if profile.location:
            location_wkt = f"SRID=4326;{profile.location.to_wkt()}"

        return cls(
            id=profile.id,
            user_id=profile.user_id,
            bio=profile.bio,
            city=profile.city,
            vehicle_type=profile.vehicle_type,
            license_category=profile.license_category,
            hourly_rate=profile.hourly_rate,
            location=location_wkt,
            rating=profile.rating,
            total_reviews=profile.total_reviews,
            is_available=profile.is_available,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    def __repr__(self) -> str:
        return f"<InstructorProfileModel(id={self.id}, user_id={self.user_id}, available={self.is_available})>"
