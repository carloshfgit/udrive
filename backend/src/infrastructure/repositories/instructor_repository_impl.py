"""
InstructorRepository Implementation

Implementação concreta do repositório de instrutores com suporte a PostGIS.
"""

from uuid import UUID

from geoalchemy2 import func as geo_func
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.instructor_profile import InstructorProfile
from src.domain.entities.location import Location
from src.domain.interfaces.instructor_repository import IInstructorRepository
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel


class InstructorRepositoryImpl(IInstructorRepository):
    """
    Implementação do repositório de instrutores usando SQLAlchemy e PostGIS.

    Utiliza queries espaciais para busca por proximidade.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, profile: InstructorProfile) -> InstructorProfile:
        """Cria um novo perfil de instrutor."""
        model = InstructorProfileModel.from_entity(profile)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, profile_id: UUID) -> InstructorProfile | None:
        """Busca perfil por ID."""
        stmt = select(InstructorProfileModel).where(
            InstructorProfileModel.id == profile_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> InstructorProfile | None:
        """Busca perfil pelo ID do usuário."""
        stmt = select(InstructorProfileModel).where(
            InstructorProfileModel.user_id == user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def update(self, profile: InstructorProfile) -> InstructorProfile:
        """Atualiza um perfil existente."""
        stmt = select(InstructorProfileModel).where(
            InstructorProfileModel.id == profile.id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Perfil não encontrado: {profile.id}")

        # Atualizar campos
        model.bio = profile.bio
        model.vehicle_type = profile.vehicle_type
        model.license_category = profile.license_category
        model.hourly_rate = profile.hourly_rate
        model.rating = profile.rating
        model.total_reviews = profile.total_reviews
        model.is_available = profile.is_available

        # Atualizar localização
        if profile.location:
            model.location = f"SRID=4326;{profile.location.to_wkt()}"
        else:
            model.location = None

        await self._session.commit()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, profile_id: UUID) -> bool:
        """Remove um perfil."""
        stmt = select(InstructorProfileModel).where(
            InstructorProfileModel.id == profile_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.commit()
        return True

    async def search_by_location(
        self,
        center: Location,
        radius_km: float = 10.0,
        only_available: bool = True,
        limit: int = 50,
    ) -> list[InstructorProfile]:
        """
        Busca instrutores por proximidade usando PostGIS.

        Utiliza ST_DWithin para busca eficiente com índice GIST.
        """
        # Converter raio de km para metros (PostGIS geography usa metros)
        radius_m = radius_km * 1000

        # Criar ponto de referência
        center_point = geo_func.ST_SetSRID(
            geo_func.ST_MakePoint(center.longitude, center.latitude),
            4326,
        )

        # Query com busca espacial
        stmt = (
            select(
                InstructorProfileModel,
                geo_func.ST_Distance(
                    geo_func.ST_Transform(InstructorProfileModel.location, 3857),
                    geo_func.ST_Transform(center_point, 3857),
                ).label("distance"),
                geo_func.ST_X(InstructorProfileModel.location).label("lon"),
                geo_func.ST_Y(InstructorProfileModel.location).label("lat"),
            )
            .where(
                InstructorProfileModel.location.isnot(None),
                geo_func.ST_DWithin(
                    geo_func.ST_Transform(InstructorProfileModel.location, 3857),
                    geo_func.ST_Transform(center_point, 3857),
                    radius_m,
                ),
            )
            .order_by("distance")
            .limit(limit)
        )

        if only_available:
            stmt = stmt.where(InstructorProfileModel.is_available.is_(True))

        result = await self._session.execute(stmt)
        rows = result.all()

        # Converter para entidades com localização
        profiles = []
        for row in rows:
            model = row[0]
            lon = row.lon
            lat = row.lat

            profile = InstructorProfile(
                id=model.id,
                user_id=model.user_id,
                bio=model.bio,
                vehicle_type=model.vehicle_type,
                license_category=model.license_category,
                hourly_rate=model.hourly_rate,
                location=Location(latitude=lat, longitude=lon) if lat and lon else None,
                rating=float(model.rating),
                total_reviews=model.total_reviews,
                is_available=model.is_available,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            profiles.append(profile)

        return profiles

    async def update_location(self, user_id: UUID, location: Location) -> bool:
        """Atualiza apenas a localização do instrutor (operação otimizada)."""
        location_wkt = f"SRID=4326;{location.to_wkt()}"

        stmt = (
            update(InstructorProfileModel)
            .where(InstructorProfileModel.user_id == user_id)
            .values(location=location_wkt)
        )

        result = await self._session.execute(stmt)
        await self._session.commit()

        return result.rowcount > 0

    async def get_available_instructors(self, limit: int = 100) -> list[InstructorProfile]:
        """Lista instrutores disponíveis."""
        stmt = (
            select(
                InstructorProfileModel,
                geo_func.ST_X(InstructorProfileModel.location).label("lon"),
                geo_func.ST_Y(InstructorProfileModel.location).label("lat"),
            )
            .where(InstructorProfileModel.is_available.is_(True))
            .order_by(InstructorProfileModel.rating.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        profiles = []
        for row in rows:
            model = row[0]
            lon = row.lon
            lat = row.lat

            profile = InstructorProfile(
                id=model.id,
                user_id=model.user_id,
                bio=model.bio,
                vehicle_type=model.vehicle_type,
                license_category=model.license_category,
                hourly_rate=model.hourly_rate,
                location=Location(latitude=lat, longitude=lon) if lat and lon else None,
                rating=float(model.rating),
                total_reviews=model.total_reviews,
                is_available=model.is_available,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            profiles.append(profile)

        return profiles

    def _model_to_entity(self, model: InstructorProfileModel) -> InstructorProfile:
        """Converte modelo para entidade (sem localização - use queries com ST_X/ST_Y)."""
        return InstructorProfile(
            id=model.id,
            user_id=model.user_id,
            bio=model.bio,
            vehicle_type=model.vehicle_type,
            license_category=model.license_category,
            hourly_rate=model.hourly_rate,
            location=None,  # Localização requer query especial
            rating=float(model.rating),
            total_reviews=model.total_reviews,
            is_available=model.is_available,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
