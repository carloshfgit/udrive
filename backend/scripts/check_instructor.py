import asyncio
from sqlalchemy import select
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel

async def check_instructor():
    async with AsyncSessionLocal() as session:
        instructor_email = "instrutor_teste@example.com"
        from src.infrastructure.db.models.user_model import UserModel
        stmt = select(InstructorProfileModel).join(UserModel).where(UserModel.email == instructor_email)
        result = await session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            print("Instrutor não encontrado.")
            return

        print(f"Instrutor ID: {model.user_id}")
        print(f"MP Access Token: {model.mp_access_token}")
        print(f"MP User ID: {model.mp_user_id}")
        
        from src.infrastructure.repositories.instructor_repository_impl import InstructorRepositoryImpl
        repo = InstructorRepositoryImpl(session)
        profile = await repo.get_by_user_id(model.user_id)
        if profile:
            print(f"Profile from Repo has MP Account: {profile.has_mp_account}")
            print(f"Profile from Repo MP Access Token: {profile.mp_access_token}")

if __name__ == "__main__":
    asyncio.run(check_instructor())
