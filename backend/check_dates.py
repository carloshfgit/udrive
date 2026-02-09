import asyncio
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.infrastructure.repositories.scheduling_repository_impl import SchedulingRepositoryImpl
from src.core.helpers.timezone_utils import DEFAULT_TIMEZONE

async def main():
    engine = create_async_engine("postgresql+asyncpg://godrive:godrive_dev_password@postgres:5432/godrive_db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        repo = SchedulingRepositoryImpl(session)
        instructor_id = UUID("67baeea5-7269-4986-9c08-52ce329f8a47")
        dates = await repo.get_scheduling_dates_for_month(instructor_id, 2026, 2)
        print("Dates for Feb 2026:", [d.isoformat() for d in dates])

if __name__ == "__main__":
    asyncio.run(main())
