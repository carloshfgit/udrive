import asyncio
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.services.auth_service_impl import AuthServiceImpl
from sqlalchemy import select

async def fix_password():
    email = "novo_instrutor@example.com"
    auth_service = AuthServiceImpl()
    hashed_password = auth_service.hash_password("password123")
    
    async with AsyncSessionLocal() as session:
        stmt = select(UserModel).where(UserModel.email == email)
        user = (await session.execute(stmt)).scalar_one_or_none()
        
        if user:
            user.hashed_password = hashed_password
            await session.commit()
            print(f"Senha de {email} atualizada para 'password123'")
        else:
            print(f"Usuário {email} não encontrado.")

if __name__ == "__main__":
    asyncio.run(fix_password())
