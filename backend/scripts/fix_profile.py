import asyncio
from decimal import Decimal
from src.infrastructure.services.token_encryption import encrypt_token
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel

async def fix():
    async with AsyncSessionLocal() as session:
        test_access_token = "APP_USR-1579574652382256-021616-3772077e1a6a378a014b0fe6f0627eb7-3207386125"
        encrypted_token = encrypt_token(test_access_token)
        
        p = InstructorProfileModel(
            user_id="49d86d02-a54a-4097-a655-2797bd53c18a",
            bio="Instrutor experiente test",
            hourly_rate=Decimal("100.00"),
            mp_access_token=encrypted_token,
            mp_user_id="2195829606"
        )
        session.add(p)
        await session.commit()
        print("Created")

if __name__ == "__main__":
    asyncio.run(fix())
