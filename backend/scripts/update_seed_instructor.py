import asyncio
from sqlalchemy import select, update
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel
from src.infrastructure.services.token_encryption import encrypt_token

async def update_instructor():
    async with AsyncSessionLocal() as session:
        instructor_email = "instrutor_teste@example.com"
        result = await session.execute(select(UserModel).where(UserModel.email == instructor_email))
        instructor = result.scalar_one_or_none()
        if not instructor:
            print("Instrutor não encontrado.")
            return

        # Um token de sandbox de um vendedor gerado anteriormente durante testes do admin
        test_access_token = "APP_USR-1579574652382256-021616-3772077e1a6a378a014b0fe6f0627eb7-3207386125"
        encrypted_token = encrypt_token(test_access_token)

        stmt = (
            update(InstructorProfileModel)
            .where(InstructorProfileModel.user_id == instructor.id)
            .values(
                mp_access_token=encrypted_token,
                mp_user_id="2195829606"
            )
        )
        await session.execute(stmt)
        await session.commit()
        print(f"Instrutor {instructor_email} atualizado com access_token encriptado.")

if __name__ == "__main__":
    asyncio.run(update_instructor())
