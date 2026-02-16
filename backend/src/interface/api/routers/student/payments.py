"""
Student Payments Router

Endpoints para operações de pagamento do aluno.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.payment_dtos import CheckoutResponseDTO, CreateCheckoutDTO
from src.application.use_cases.payment import (
    CalculateSplitUseCase,
    CreateCheckoutUseCase,
)
from src.domain.exceptions import (
    DomainException,
    PaymentAlreadyProcessedException,
    PaymentFailedException,
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
from src.interface.api.dependencies import CurrentStudent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Student - Payments"])


@router.post(
    "/checkout",
    response_model=CheckoutResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Criar checkout de pagamento",
    description="Cria uma preferência de pagamento no Mercado Pago e retorna a URL de checkout.",
)
async def checkout(
    dto: CreateCheckoutDTO,
    current_user: CurrentStudent,
    db: AsyncSession = Depends(get_db),
) -> CheckoutResponseDTO:
    """
    Endpoint para criar checkout via Mercado Pago Checkout Pro.
    Apenas alunos podem iniciar pagamento.
    Retorna a URL de checkout para redirecionar o aluno ao Mercado Pago.
    """
    # Validação de segurança: aluno só pode pagar por si
    if dto.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não autorizado a processar pagamento para outro usuário",
        )

    # Dependências
    settings = Settings()
    use_case = CreateCheckoutUseCase(
        scheduling_repository=SchedulingRepositoryImpl(db),
        payment_repository=PaymentRepositoryImpl(db),
        transaction_repository=TransactionRepositoryImpl(db),
        instructor_repository=InstructorRepositoryImpl(db),
        payment_gateway=MercadoPagoGateway(settings),
        calculate_split_use_case=CalculateSplitUseCase(),
        settings=settings,
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
    except PaymentFailedException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        ) from e
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        logger.error("Erro no checkout: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar pagamento",
        ) from e
