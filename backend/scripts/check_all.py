import asyncio
from sqlalchemy import select
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel

async def check():
    async with AsyncSessionLocal() as session:
        # Check all instructors users
        stmt = select(UserModel).where(UserModel.user_type == "instructor")
        result = await session.execute(stmt)
        users = result.scalars().all()
        print(f"Instructors users count: {len(users)}")
        
        # Check all profiles
        stmt = select(InstructorProfileModel)
        result = await session.execute(stmt)
        profiles = result.scalars().all()
        print(f"Instructor profiles count: {len(profiles)}")
        for p in profiles:
            print(f"- Profile user_id: {p.user_id}, MP token: {bool(p.mp_access_token)}")

        # Print the one from generate_test_checkout (if exists)
        instructor_email = "instrutor_teste@example.com"
        stmt = select(UserModel).where(UserModel.email == instructor_email)
        res = await getattr(session, "execute")(stmt)
        u = res.scalar_one_or_none()
        print(f"\nUser {instructor_email}: {'Found' if u else 'Not found'} id={u.id if u else None}")

if __name__ == "__main__":
    asyncio.run(check())
