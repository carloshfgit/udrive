"""
Payments Router

Endpoints para operações de pagamento.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import (
    GetPaymentHistoryDTO,
    PaymentHistoryResponseDTO,
    PaymentResponseDTO,
    ProcessPaymentDTO,
)
from src.application.use_cases.payment import (
    CalculateSplitUseCase,
    GetPaymentHistoryUseCase,
    ProcessPaymentUseCase,
)
from src.domain.exceptions import (
    DomainException,
    PaymentAlreadyProcessedException,
    SchedulingNotFoundException,
    StripeAccountNotConnectedException,
    UserNotFoundException,
)
from src.infrastructure.db.database import get_db
from src.infrastructure.external.stripe_gateway import StripePaymentGateway
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
from src.interface.api.dependencies import CurrentUser, get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/checkout",
    response_model=PaymentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Processar pagamento de aula",
    description="Inicia o processo de pagamento utilizando Stripe com split atômico.",
)
async def checkout(
    dto: ProcessPaymentDTO,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> PaymentResponseDTO:
    """
    Endpoint para realizar checkout.
    Apenas alunos podem iniciar pagamento (validar no use case ou aqui).
    """
    # Dependências
    scheduling_repo = SchedulingRepositoryImpl(db)
    payment_repo = PaymentRepositoryImpl(db)
    transaction_repo = TransactionRepositoryImpl(db)
    instructor_repo = InstructorRepositoryImpl(db)
    user_repo = UserRepositoryImpl(db)
    payment_gateway = StripePaymentGateway()
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

    # Forçar ID do aluno logado para segurança (sobrescrever DTO se necessário)
    # ou validar que DTO.student_id == current_user.id
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
        StripeAccountNotConnectedException,
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


@router.get(
    "/history",
    response_model=PaymentHistoryResponseDTO,
    summary="Histórico de pagamentos",
    description="Retorna histórico de pagamentos do usuário atual (aluno ou instrutor).",
)
async def get_payment_history(
    current_user: CurrentUser,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> PaymentHistoryResponseDTO:
    """Histórico financeiro."""
    user_repo = UserRepositoryImpl(db)
    payment_repo = PaymentRepositoryImpl(db)
    scheduling_repo = SchedulingRepositoryImpl(db)

    use_case = GetPaymentHistoryUseCase(
        user_repository=user_repo,
        payment_repository=payment_repo,
        scheduling_repository=scheduling_repo,
    )

    dto = GetPaymentHistoryDTO(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )

    try:
        return await use_case.execute(dto)
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request):
    """
    Webhook para receber atualizações do Stripe.
    A ser implementado completamente para tratar:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    """
    # TODO: Implementar lógica de validação de assinatura e processamento de eventos
    # Isso requer STRIPE_WEBHOOK_SECRET e parsing do body raw
    return {"status": "received"}
