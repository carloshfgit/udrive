import asyncio
import sys
from sqlalchemy import select
from src.infrastructure.db.database import AsyncSessionLocal
from src.infrastructure.db.models.user_model import UserModel
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel
from src.infrastructure.services.token_encryption import encrypt_token

async def update_token():
    email = sys.argv[1] if len(sys.argv) > 1 else 'instrutor_teste@example.com'
    
    async with AsyncSessionLocal() as session:
        # Busca o usuário pelo email
        stmt = select(UserModel).where(UserModel.email == email)
        user = (await session.execute(stmt)).scalar_one_or_none()
        
        if not user:
            print(f"Erro: Usuário com email '{email}' não encontrado.")
            return

        # Token do .env (fallback) ou sandbox
        test_access_token = "APP_USR-1579574652382256-021616-3772077e1a6a378a014b0fe6f0627eb7-3207386125"
        encrypted_token = encrypt_token(test_access_token)
        mp_user_id = "2195829606"

        # Verifica se já tem perfil
        stmt_prof = select(InstructorProfileModel).where(InstructorProfileModel.user_id == user.id)
        profile = (await session.execute(stmt_prof)).scalar_one_or_none()

        if profile:
            profile.mp_access_token = encrypted_token
            profile.mp_user_id = mp_user_id
            print(f"Perfil de {email} atualizado.")
        else:
            profile = InstructorProfileModel(
                user_id=user.id,
                mp_access_token=encrypted_token,
                mp_user_id=mp_user_id,
                hourly_rate=100.0, # Valor padrão para teste
                license_category="B",
                is_available=True
            )
            session.add(profile)
            print(f"Perfil de {email} criado com o token.")
        
        await session.commit()
        print(f"Sucesso: {email} pronto para testes do Mercado Pago.")


if __name__ == "__main__":
    asyncio.run(update_token())
