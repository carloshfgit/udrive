"""
Instructor Earnings Router

Endpoints para informações financeiras do instrutor.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import (
    ConnectGatewayAccountDTO,
    InstructorEarningsDTO,
    GatewayConnectResponseDTO,
)
from src.application.use_cases.payment import (
    ConnectGatewayAccountUseCase,
    GetInstructorEarningsUseCase,
)
from src.domain.exceptions import InstructorNotFoundException, UserNotFoundException
from src.infrastructure.db.database import get_db
from src.infrastructure.config import Settings
from src.infrastructure.external.mercadopago_gateway import MercadoPagoGateway
from src.infrastructure.repositories.payment_repository_impl import (
    PaymentRepositoryImpl,
)
from src.interface.api.dependencies import CurrentInstructor, InstructorRepo, UserRepo

router = APIRouter(tags=["Instructor - Earnings"])


@router.post(
    "/gateway/connect",
    response_model=GatewayConnectResponseDTO,
    summary="Conectar conta de pagamento",
    description="Gera link de redirecionamento para autorização da conta de pagamento do instrutor.",
)
async def connect_gateway_account(
    dto: ConnectGatewayAccountDTO,
    current_user: CurrentInstructor,
    user_repo: UserRepo,
    instructor_repo: InstructorRepo,
) -> GatewayConnectResponseDTO:
    """Conecta conta de pagamento."""
    settings = Settings()
    payment_gateway = MercadoPagoGateway(settings)

    use_case = ConnectGatewayAccountUseCase(
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
