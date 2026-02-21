import asyncio
import sys
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from decimal import Decimal

from src.infrastructure.db.database import AsyncSessionLocal
from src.application.use_cases.payment.create_checkout import CreateCheckoutUseCase
from src.infrastructure.repositories.scheduling_repository_impl import SchedulingRepositoryImpl
from src.infrastructure.repositories.payment_repository_impl import PaymentRepositoryImpl
from src.infrastructure.repositories.transaction_repository_impl import TransactionRepositoryImpl
from src.infrastructure.repositories.instructor_repository_impl import InstructorRepositoryImpl
from src.infrastructure.external.mercadopago_gateway import MercadoPagoGateway
from src.application.use_cases.payment.calculate_split import CalculateSplitUseCase
from src.infrastructure.config import Settings
from src.application.dtos.payment_dtos import CreateCheckoutDTO
from sqlalchemy import select
from src.infrastructure.db.models.scheduling_model import SchedulingModel
from src.infrastructure.db.models.instructor_profile_model import InstructorProfileModel
from src.infrastructure.db.models.user_model import UserModel

async def generate():
    instructor_email = sys.argv[1] if len(sys.argv) > 1 else None
    
    settings = Settings()
    
    async with AsyncSessionLocal() as session:
        # 1. Buscar um agendamento pendente
        # Se email for passado, busca especificamente desse instrutor
        query = select(SchedulingModel).where(SchedulingModel.status == "pending")
        
        if instructor_email:
            # Join com User para filtrar por email
            user_stmt = select(UserModel.id).where(UserModel.email == instructor_email)
            user_id = (await session.execute(user_stmt)).scalar_one_or_none()
            if not user_id:
                print(f"Erro: Instrutor '{instructor_email}' não encontrado.")
                return
            query = query.where(SchedulingModel.instructor_id == user_id)

        scheduling = (await session.execute(query.limit(1))).scalar_one_or_none()
        if not scheduling:
            print("Nenhum agendamento 'pending' encontrado no banco.")
            return

        student_id = scheduling.student_id
        scheduling_id = scheduling.id
        
        use_case = CreateCheckoutUseCase(
            scheduling_repository=SchedulingRepositoryImpl(session),
            payment_repository=PaymentRepositoryImpl(session),
            transaction_repository=TransactionRepositoryImpl(session),
            instructor_repository=InstructorRepositoryImpl(session),
            payment_gateway=MercadoPagoGateway(settings),
            calculate_split_use_case=CalculateSplitUseCase(),
            settings=settings,
        )
        
        dto = CreateCheckoutDTO(
            scheduling_ids=[scheduling_id],
            student_id=student_id,
            student_email="aluno_teste@example.com"
        )
        
        try:
            result = await use_case.execute(dto)
            print("\n--- CHECKOUT GERADO ---")
            print(f"Payment ID: {result.payment_id}")
            print(f"Preference ID: {result.preference_id}")
            print(f"Checkout URL: {result.checkout_url}")
            if result.sandbox_url:
                print(f"Sandbox URL: {result.sandbox_url}")
            print("------------------------")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"\nErro original: {e}")

        async with AsyncSessionLocal() as session:
            stmt = select(InstructorProfileModel).where(InstructorProfileModel.user_id == '49d86d02-a54a-4097-a655-2797bd53c18a')
            prof = (await session.execute(stmt)).scalar_one_or_none()
            if prof:
                print("RAW DB TOKEN:", prof.mp_access_token)
                from src.infrastructure.services.token_encryption import decrypt_token 
                print("DECRYPTED:", decrypt_token(prof.mp_access_token))
        
if __name__ == "__main__":
    asyncio.run(generate())
