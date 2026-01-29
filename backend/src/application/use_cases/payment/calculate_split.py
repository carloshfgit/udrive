"""
Calculate Split Use Case

Caso de uso para calcular a divisão do pagamento entre plataforma e instrutor.
"""

from dataclasses import dataclass
from decimal import Decimal

from src.application.dtos.payment_dtos import SplitCalculationDTO


# Taxa padrão da plataforma (15%)
DEFAULT_PLATFORM_FEE_PERCENTAGE = Decimal("15.00")


@dataclass
class CalculateSplitUseCase:
    """
    Caso de uso para calcular o split de pagamento.

    Divide o valor total entre a plataforma e o instrutor com base
    na taxa configurada.

    Fluxo:
        1. Receber valor total da aula
        2. Aplicar taxa da plataforma
        3. Calcular valor líquido para o instrutor
        4. Retornar SplitCalculationDTO
    """

    platform_fee_percentage: Decimal = DEFAULT_PLATFORM_FEE_PERCENTAGE

    def execute(self, total_amount: Decimal) -> SplitCalculationDTO:
        """
        Executa o cálculo do split.

        Args:
            total_amount: Valor total do pagamento em BRL.

        Returns:
            SplitCalculationDTO: Resultado do cálculo com valores divididos.

        Raises:
            ValueError: Se o valor total for negativo.
        """
        if total_amount < 0:
            raise ValueError("Valor total não pode ser negativo")

        if total_amount == Decimal("0.00"):
            return SplitCalculationDTO(
                total_amount=Decimal("0.00"),
                platform_fee_percentage=self.platform_fee_percentage,
                platform_fee_amount=Decimal("0.00"),
                instructor_amount=Decimal("0.00"),
            )

        # Calcula taxa da plataforma
        platform_fee_amount = (
            total_amount * self.platform_fee_percentage / Decimal("100")
        ).quantize(Decimal("0.01"))

        # Valor líquido do instrutor
        instructor_amount = total_amount - platform_fee_amount

        return SplitCalculationDTO(
            total_amount=total_amount,
            platform_fee_percentage=self.platform_fee_percentage,
            platform_fee_amount=platform_fee_amount,
            instructor_amount=instructor_amount,
        )
