"""
Calculate Split Use Case

Caso de uso para calcular a divisão do pagamento entre plataforma e instrutor.
"""

from dataclasses import dataclass
from decimal import Decimal

from src.application.dtos.payment_dtos import SplitCalculationDTO


from src.infrastructure.config import settings

from src.infrastructure.services.pricing_service import PricingService

@dataclass
class CalculateSplitUseCase:
    """
    Caso de uso para calcular o split de pagamento.

    Divide o valor total entre a plataforma e o instrutor.
    Agora suporta o modelo fee-on-top, onde o instrutor recebe um valor base
    e a plataforma fica com a diferença (incluindo arredondamentos).
    """

    def execute(
        self, total_amount: Decimal, instructor_base_amount: Decimal | None = None
    ) -> SplitCalculationDTO:
        """
        Executa o cálculo do split.

        Args:
            total_amount: Valor total pago pelo aluno (final_price).
            instructor_base_amount: Valor base que o instrutor deve receber (opcional).

        Returns:
            SplitCalculationDTO: Resultado do cálculo.
        """
        if total_amount < 0:
            raise ValueError("Valor total não pode ser negativo")

        if total_amount == Decimal("0.00"):
            return SplitCalculationDTO(
                total_amount=Decimal("0.00"),
                platform_fee_percentage=Decimal("0.00"),
                platform_fee_amount=Decimal("0.00"),
                instructor_amount=Decimal("0.00"),
            )

        # Se tivermos o valor base, usamos a nova lógica fee-on-top
        if instructor_base_amount is not None:
            # A platform_fee_amount (marketplace_fee no gateway) é calculada para
            # garantir que o instrutor receba o instructor_base_amount líquido.
            platform_fee_amount = PricingService.calculate_marketplace_fee(
                total_amount, instructor_base_amount
            )
            
            # O instructor_amount aqui representa o que o instrutor "vê" como seu ganho
            # Mas lembre-se: no MP, ele recebe total_amount e o MP tira marketplace_fee dele.
            # Então ele fica com (total_amount - marketplace_fee). Após pagar a taxa do MP,
            # ele deve ficar com exatamente o instructor_base_amount.
            instructor_amount = total_amount - platform_fee_amount
        else:
            # Lógica legada/proporcional (usada em contextos onde não há valor base fixo)
            fee_percentage = Decimal(str(settings.platform_fee_percentage))
            platform_fee_amount = (
                total_amount * fee_percentage / Decimal("100")
            ).quantize(Decimal("0.01"))
            instructor_amount = total_amount - platform_fee_amount

        return SplitCalculationDTO(
            total_amount=total_amount,
            platform_fee_percentage=Decimal("0.00"),  # Não é mais baseado em % fixo
            platform_fee_amount=platform_fee_amount,
            instructor_amount=instructor_amount,
        )
