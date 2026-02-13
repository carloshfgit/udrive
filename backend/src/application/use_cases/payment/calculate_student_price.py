"""
Calculate Student Price Use Case

Caso de uso para calcular o preço final all-inclusive para o aluno.
O modelo garante que o instrutor receba exatamente o valor definido.
"""

import math
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from src.application.dtos.payment_dtos import StudentPriceDTO
from src.infrastructure.config import settings

# Taxas Stripe (Brasil)
STRIPE_CARD_PERCENTAGE = Decimal("0.0399")  # 3.99%
STRIPE_CARD_FIXED = Decimal("0.39")  # R$ 0,39
STRIPE_PIX_PERCENTAGE = Decimal("0.0119")  # 1.19%

TWO_PLACES = Decimal("0.01")


@dataclass
class CalculateStudentPriceUseCase:
    """
    Calcula o preço final que o aluno pagará.

    Composição:
        total = preço_instrutor + comissão_13% + taxas_stripe

    O cálculo usa fórmula reversa para que, após o Stripe descontar
    suas taxas, o valor líquido cubra exatamente o preço base + comissão.
    """

    def execute(
        self,
        instructor_rate: Decimal,
        payment_method: str = "card",
    ) -> StudentPriceDTO:
        """
        Executa o cálculo de preço all-inclusive.

        Args:
            instructor_rate: Valor por aula definido pelo instrutor.
            payment_method: "card" ou "pix".

        Returns:
            StudentPriceDTO com breakdown completo.

        Raises:
            ValueError: Se valor for negativo ou método inválido.
        """
        if instructor_rate < 0:
            raise ValueError("Valor do instrutor não pode ser negativo")

        if payment_method not in ("card", "pix"):
            raise ValueError(
                f"Método de pagamento inválido: {payment_method}. Use 'card' ou 'pix'."
            )

        # Comissão da plataforma (valor do env sobre preço do instrutor)
        platform_fee_pct = Decimal(str(settings.platform_fee_percentage)) / Decimal("100")
        platform_fee = (instructor_rate * platform_fee_pct).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

        # Subtotal antes do Stripe
        subtotal = instructor_rate + platform_fee

        # Cálculo da taxa Stripe (fórmula reversa para cartão)
        if payment_method == "card":
            # total = (subtotal + fixed) / (1 - percentage)
            # stripe_fee = total - subtotal
            total = (
                (subtotal + STRIPE_CARD_FIXED)
                / (Decimal("1") - STRIPE_CARD_PERCENTAGE)
            ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            stripe_fee = total - subtotal
        else:
            # PIX: taxa simples de 1.19%
            stripe_fee = (subtotal * STRIPE_PIX_PERCENTAGE).quantize(
                TWO_PLACES, rounding=ROUND_HALF_UP
            )
            total = subtotal + stripe_fee

        # Arredondamento para o próximo múltiplo de 5 (sempre para cima)
        raw_total = total
        total_rounded = Decimal(math.ceil(total / 5) * 5)

        # Charm pricing: se múltiplo de 10, subtrai R$ 0,10 (ex: 100 → 99,90)
        if total_rounded % 10 == 0:
            total_rounded -= Decimal("0.10")

        # Surplus do arredondamento é absorvido pela comissão da plataforma
        surplus = (total_rounded - raw_total).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )
        platform_fee += surplus
        total = total_rounded

        return StudentPriceDTO(
            instructor_amount=instructor_rate,
            platform_fee_amount=platform_fee,
            stripe_fee_estimate=stripe_fee,
            total_student_price=total,
            payment_method=payment_method,
            rounding_surplus=surplus,
        )
