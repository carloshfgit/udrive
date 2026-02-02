"""
Instructor Earnings Router

Endpoints para informações financeiras do instrutor.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import (
    ConnectStripeAccountDTO,
    InstructorEarningsDTO,
    StripeConnectResponseDTO,
)
from src.application.use_cases.payment import (
    ConnectStripeAccountUseCase,
    GetInstructorEarningsUseCase,
)
from src.domain.exceptions import InstructorNotFoundException, UserNotFoundException
from src.infrastructure.db.database import get_db
from src.infrastructure.external.stripe_gateway import StripePaymentGateway
from src.infrastructure.repositories.payment_repository_impl import (
    PaymentRepositoryImpl,
)
from src.interface.api.dependencies import CurrentInstructor, InstructorRepo, UserRepo

router = APIRouter(tags=["Instructor - Earnings"])


@router.post(
    "/stripe/connect",
    response_model=StripeConnectResponseDTO,
    summary="Conectar conta Stripe",
    description="Gera link de onboarding para conta Stripe Connect do instrutor.",
)
async def connect_stripe_account(
    dto: ConnectStripeAccountDTO,
    current_user: CurrentInstructor,
    user_repo: UserRepo,
    instructor_repo: InstructorRepo,
) -> StripeConnectResponseDTO:
    """Conecta conta Stripe."""
    payment_gateway = StripePaymentGateway()

    use_case = ConnectStripeAccountUseCase(
        user_repository=user_repo,
        instructor_repository=instructor_repo,
        payment_gateway=payment_gateway,
    )

    # Forçar ID
    if dto.instructor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Proibido")

    try:
        return await use_case.execute(dto)
    except (UserNotFoundException, InstructorNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.get(
    "/earnings",
    response_model=InstructorEarningsDTO,
    summary="Obter ganhos",
    description="Retorna resumo financeiro do instrutor.",
)
async def get_instructor_earnings(
    current_user: CurrentInstructor,
    instructor_repo: InstructorRepo,
    db: AsyncSession = Depends(get_db),
) -> InstructorEarningsDTO:
    """Obtém ganhos do instrutor."""
    payment_repo = PaymentRepositoryImpl(db)

    use_case = GetInstructorEarningsUseCase(
        instructor_repository=instructor_repo,
        payment_repository=payment_repo,
    )

    try:
        return await use_case.execute(str(current_user.id))
    except InstructorNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
