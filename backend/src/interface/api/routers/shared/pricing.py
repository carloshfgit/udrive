"""
Shared Pricing Router

Endpoint de cálculo de preço para exibição no frontend.
"""

from decimal import Decimal

from fastapi import APIRouter, Query

from src.application.dtos.payment_dtos import StudentPriceDTO
from src.application.use_cases.payment.calculate_student_price import (
    CalculateStudentPriceUseCase,
)

router = APIRouter(prefix="/pricing", tags=["Shared - Pricing"])


@router.get(
    "/calculate",
    response_model=StudentPriceDTO,
    summary="Calcular preço final para o aluno",
    description=(
        "Retorna o breakdown completo do preço: valor do instrutor, "
        "comissão da plataforma (20%), estimativa de taxas Stripe e total final."
    ),
)
async def calculate_price(
    instructor_rate: float = Query(
        ...,
        gt=0,
        description="Valor por aula definido pelo instrutor (em BRL)",
    ),
    payment_method: str = Query(
        "card",
        pattern="^(card|pix)$",
        description="Método de pagamento: 'card' ou 'pix'",
    ),
) -> StudentPriceDTO:
    """Calcula o preço all-inclusive para o aluno."""
    use_case = CalculateStudentPriceUseCase()

    return use_case.execute(
        instructor_rate=Decimal(str(instructor_rate)),
        payment_method=payment_method,
    )
