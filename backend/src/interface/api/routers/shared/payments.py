"""
Shared Payments Router

Endpoints de pagamento compartilhados entre alunos e instrutores.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import (
    GetPaymentHistoryDTO,
    PaymentHistoryResponseDTO,
)
from src.application.use_cases.payment import GetPaymentHistoryUseCase
from src.domain.exceptions import UserNotFoundException
from src.infrastructure.db.database import get_db
from src.infrastructure.repositories.payment_repository_impl import (
    PaymentRepositoryImpl,
)
from src.infrastructure.repositories.scheduling_repository_impl import (
    SchedulingRepositoryImpl,
)
from src.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from src.interface.api.dependencies import CurrentUser

router = APIRouter(prefix="/payments", tags=["Shared - Payments"])


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
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request):
    """
    Webhook para receber atualizações do Stripe.
    A ser implementado completamente para tratar:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    """
    # TODO: Implementar lógica de validação de assinatura e processamento de eventos
    return {"status": "received"}
