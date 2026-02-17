import asyncio
from uuid import UUID
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

async def generate():
    # IDs from the seed output - replacing with current values
    student_id = UUID('84175e57-f9f2-4760-a774-a49c520a289c')
    scheduling_id = UUID('b9ca64ed-aae5-4e60-ada8-6a105ce87e69')
    
    settings = Settings()
    
    async with AsyncSessionLocal() as session:
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
            scheduling_id=scheduling_id,
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
            print(f"\nErro ao gerar checkout: {e}")

if __name__ == "__main__":
    asyncio.run(generate())
