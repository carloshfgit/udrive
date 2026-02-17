import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel
from src.infrastructure.db.models.student_profile_model import StudentProfileModel
from src.infrastructure.db.models.scheduling_model import SchedulingModel
from src.domain.entities.user_type import UserType
from src.domain.entities.scheduling_status import SchedulingStatus
from src.infrastructure.services.auth_service_impl import AuthServiceImpl

async def seed():
    auth_service = AuthServiceImpl()
    hashed_password = auth_service.hash_password("password123")
    
    async with AsyncSessionLocal() as session:
        # 1. Create Student
        student_email = "aluno_teste@example.com"
        result = await session.execute(select(UserModel).where(UserModel.email == student_email))
        student = result.scalar_one_or_none()
        
        if not student:
            student = UserModel(
                id=uuid.uuid4(),
                email=student_email,
                hashed_password=hashed_password,
                full_name="Aluno de Teste",
                user_type=UserType.STUDENT.value,
                is_active=True,
                is_verified=True
            )
            session.add(student)
            await session.flush()
            
            student_profile = StudentProfileModel(
                user_id=student.id,
            )
            session.add(student_profile)
            print(f"Student created: {student_email}")
        else:
            print(f"Student already exists: {student_email}")

        # 2. Create Instructor
        instructor_email = "instrutor_teste@example.com"
        result = await session.execute(select(UserModel).where(UserModel.email == instructor_email))
        instructor = result.scalar_one_or_none()
        
        if not instructor:
            instructor = UserModel(
                id=uuid.uuid4(),
                email=instructor_email,
                hashed_password=hashed_password,
                full_name="Instrutor de Teste",
                user_type=UserType.INSTRUCTOR.value,
                is_active=True,
                is_verified=True
            )
            session.add(instructor)
            await session.flush()
            
            instructor_profile = InstructorProfileModel(
                user_id=instructor.id,
                bio="Instrutor experiente para testes.",
                hourly_rate=Decimal("100.00"),
                # has_mp_account is a property of the ENTITY, not the MODEL
                mp_access_token="APP_USR-1579574652382256-021616-3772077e1a6a378a014b0fe6f0627eb7-3207386125",
                mp_user_id="3207386125"
            )
            session.add(instructor_profile)
            print(f"Instructor created: {instructor_email}")
        else:
             print(f"Instructor already exists: {instructor_email}")

        # 3. Create Scheduling
        scheduled_at = datetime.now() + timedelta(days=1)
        
        scheduling = SchedulingModel(
            id=uuid.uuid4(),
            student_id=student.id,
            instructor_id=instructor.id,
            scheduled_datetime=scheduled_at,
            duration_minutes=60,
            price=Decimal("100.00"),
            status=SchedulingStatus.PENDING
        )
        session.add(scheduling)
        await session.commit()
        
        print(f"Scheduling created with ID: {scheduling.id}")
        print("\n--- TEST DATA ---")
        print(f"Student ID: {student.id}")
        print(f"Instructor ID: {instructor.id}")
        print(f"Scheduling ID: {scheduling.id}")
        print(f"Student Login: {student_email} / password123")
        print("-----------------")

if __name__ == "__main__":
    asyncio.run(seed())
