
import asyncio
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.infrastructure.config import settings
from src.infrastructure.db.database import Base
from src.infrastructure.db.models.review_model import ReviewModel
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel
from src.infrastructure.db.models.user_model import UserModel

async def check_reviews():
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check all reviews
        result = await session.execute(select(ReviewModel))
        reviews = result.scalars().all()
        print(f"Total reviews in DB: {len(reviews)}")
        for r in reviews:
            stmt = select(UserModel).where(UserModel.id == r.student_id)
            stu_res = await session.execute(stmt)
            stu = stu_res.scalar_one_or_none()
            print(f"Review: ID={r.id}, InstructorID={r.instructor_id}, StudentID={r.student_id}, StudentName={stu.full_name if stu else 'N/A'}, Comment={r.comment}")
            
        # Check an instructor
        result = await session.execute(select(InstructorProfileModel))
        profiles = result.scalars().all()
        for p in profiles:
            print(f"Instructor: UserID={p.user_id}, Name={p.user_id}")

if __name__ == "__main__":
    asyncio.run(check_reviews())
