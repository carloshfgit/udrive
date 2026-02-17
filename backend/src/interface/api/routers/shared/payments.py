"""
Shared Payments Router

Endpoints de pagamento compartilhados entre alunos e instrutores.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import (
    CancelSchedulingDTO,
    CancelSchedulingResultDTO,
    GetPaymentHistoryDTO,
    PaymentHistoryResponseDTO,
)
from src.application.use_cases.payment import GetPaymentHistoryUseCase
from src.application.use_cases.payment.cancel_scheduling import (
    CancelSchedulingUseCase,
)
from src.application.use_cases.payment.process_refund import ProcessRefundUseCase
from src.domain.exceptions import (
    CancellationException,
    RefundException,
    SchedulingNotFoundException,
    UserNotFoundException,
)
from src.infrastructure.db.database import get_db
from src.infrastructure.external import MercadoPagoGateway
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


@router.post(
    "/cancel",
    response_model=CancelSchedulingResultDTO,
    summary="Cancelar agendamento",
    description="Cancela agendamento e processa reembolso conforme regras.",
)
async def cancel_scheduling(
    current_user: CurrentUser,
    scheduling_id: str,
    reason: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> CancelSchedulingResultDTO:
    """Cancela agendamento com reembolso automático."""
    from uuid import UUID

    scheduling_repo = SchedulingRepositoryImpl(db)
    payment_repo = PaymentRepositoryImpl(db)
    transaction_repo = TransactionRepositoryImpl(db)
    instructor_repo = InstructorRepositoryImpl(db)
    gateway = MercadoPagoGateway()

    process_refund = ProcessRefundUseCase(
        payment_repository=payment_repo,
        transaction_repository=transaction_repo,
        instructor_repository=instructor_repo,
        payment_gateway=gateway,
    )

    use_case = CancelSchedulingUseCase(
        scheduling_repository=scheduling_repo,
        payment_repository=payment_repo,
        process_refund_use_case=process_refund,
    )

    dto = CancelSchedulingDTO(
        scheduling_id=UUID(scheduling_id),
        cancelled_by=current_user.id,
        reason=reason,
    )

    try:
        return await use_case.execute(dto)
    except SchedulingNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except CancellationException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RefundException as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

