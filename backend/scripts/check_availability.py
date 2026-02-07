
import asyncio
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Configuração simples para rodar via docker exec ou localmente se o DB estiver exposto
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://godrive:godrive_dev_password@localhost:5432/godrive_db")

async def check_availability(instructor_id: str):
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    from src.infrastructure.db.models.availability_model import AvailabilityModel
    
    async with async_session() as session:
        stmt = select(AvailabilityModel).where(AvailabilityModel.instructor_id == UUID(instructor_id))
        result = await session.execute(stmt)
        availabilities = result.scalars().all()
        
        print(f"Availability for instructor {instructor_id}:")
        for a in availabilities:
            print(f"- Day {a.day_of_week}: {a.start_time} - {a.end_time} (Active: {a.is_active})")

if __name__ == "__main__":
    instructor_id = "67baeea5-7269-4986-9c08-52ce329f8a47"
    asyncio.run(check_availability(instructor_id))
