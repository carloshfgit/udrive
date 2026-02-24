import asyncio
from src.infrastructure.db.database import get_db

async def check():
    async for db in get_db():
        from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
        repo = UserRepositoryImpl(db)
        user = await repo.get_by_email("TESTUSER8917601619045298291")
        print(f"User found: {user}")

asyncio.run(check())
