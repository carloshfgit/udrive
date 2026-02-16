"""
Student Payments Router

Endpoints para operações de pagamento do aluno.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import PaymentResponseDTO, ProcessPaymentDTO
from src.application.use_cases.payment import (
    CalculateSplitUseCase,
    ProcessPaymentUseCase,
)
from src.domain.exceptions import (
    DomainException,
    PaymentAlreadyProcessedException,
    SchedulingNotFoundException,
    GatewayAccountNotConnectedException,
)
from src.infrastructure.db.database import get_db
from src.infrastructure.config import Settings
from src.infrastructure.external.mercadopago_gateway import MercadoPagoGateway
from src.infrastructure.repositories.instructor_repository_impl import (
    InstructorRepositoryImpl,
)
from src.infrastructure.repositories.payment_repository_impl import (
    PaymentRepositoryImpl,
)
from src.infrastructure.repositories.scheduling_repository_impl import (
    SchedulingRepositoryImpl,
)
from src.infrastructure.repositories.transaction_repository_impl import (
    TransactionRepositoryImpl,
)
from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from src.interface.api.dependencies import CurrentStudent

router = APIRouter(prefix="/payments", tags=["Student - Payments"])


@router.post(
    "/checkout",
    response_model=PaymentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Processar pagamento de aula",
    description="Inicia o processo de pagamento utilizando o gateway configurado (ex: Mercado Pago).",
)
async def checkout(
    dto: ProcessPaymentDTO,
    current_user: CurrentStudent,
    db: AsyncSession = Depends(get_db),
) -> PaymentResponseDTO:
    """
    Endpoint para realizar checkout.
    Apenas alunos podem iniciar pagamento.
    """
    # Dependências
    scheduling_repo = SchedulingRepositoryImpl(db)
    payment_repo = PaymentRepositoryImpl(db)
    transaction_repo = TransactionRepositoryImpl(db)
    instructor_repo = InstructorRepositoryImpl(db)
    user_repo = UserRepositoryImpl(db)
    settings = Settings()
    payment_gateway = MercadoPagoGateway(settings)
    calculate_split = CalculateSplitUseCase()

    use_case = ProcessPaymentUseCase(
        scheduling_repository=scheduling_repo,
        payment_repository=payment_repo,
        transaction_repository=transaction_repo,
        instructor_repository=instructor_repo,
        user_repository=user_repo,
        payment_gateway=payment_gateway,
        calculate_split_use_case=calculate_split,
    )

    # Forçar ID do aluno logado para segurança
    if dto.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a processar pagamento para outro usuário",
        )

    try:
        return await use_case.execute(dto)
    except SchedulingNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except (
        PaymentAlreadyProcessedException,
        GatewayAccountNotConnectedException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        import logging

        logging.error(f"Erro no checkout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar pagamento",
        ) from e
