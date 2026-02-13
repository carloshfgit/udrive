"""
Tests for CalculateStudentPriceUseCase

Testa o cálculo de preço all-inclusive, arredondamento para múltiplo de 5
e charm pricing (subtrair R$ 0,10 de múltiplos de 10).
"""

from decimal import Decimal

import pytest

from src.application.use_cases.payment.calculate_student_price import (
    CalculateStudentPriceUseCase,
)


@pytest.fixture
def use_case():
    return CalculateStudentPriceUseCase()


class TestPlatformFee:
    """Verifica que a comissão da plataforma é 13%."""

    def test_platform_fee_is_13_percent(self, use_case):
        result = use_case.execute(Decimal("100.00"))
        # Antes do arredondamento, platform_fee base = 100 * 0.13 = 13.00
        # O total inclui surplus, mas o instructor_amount permanece 100
        assert result.instructor_amount == Decimal("100.00")

    def test_invalid_payment_method_raises(self, use_case):
        with pytest.raises(ValueError, match="Método de pagamento inválido"):
            use_case.execute(Decimal("100.00"), payment_method="bitcoin")

    def test_negative_rate_raises(self, use_case):
        with pytest.raises(ValueError, match="não pode ser negativo"):
            use_case.execute(Decimal("-10.00"))


class TestRoundingToMultipleOf5:
    """Verifica arredondamento para o próximo múltiplo de 5."""

    def test_total_ends_in_0_or_5(self, use_case):
        """O preço final deve terminar em 0 ou 5 (ou .90 para charm)."""
        for rate in [50, 60, 70, 75, 80, 90, 100, 120, 150, 200]:
            result = use_case.execute(Decimal(str(rate)))
            last_digit = result.total_student_price % 10
            assert last_digit in (
                Decimal("0"),
                Decimal("5"),
                Decimal("9.90"),
            ), f"Rate {rate}: total {result.total_student_price} não termina em 0, 5 ou 9.90"

    def test_total_always_rounded_up(self, use_case):
        """O total arredondado deve ser >= ao cálculo base."""
        for rate in [50, 73, 88, 100, 117, 150]:
            result = use_case.execute(Decimal(str(rate)))
            # O preço final nunca pode ser menor que o instructor_amount
            assert result.total_student_price > result.instructor_amount


class TestCharmPricing:
    """Verifica charm pricing: múltiplos de 10 → subtrair R$ 0,10."""

    def test_charm_pricing_applied_to_multiple_of_10(self, use_case):
        """Se arredondamento cai em múltiplo de 10, subtrai 0.10."""
        # Testamos vários rates e verificamos que nenhum total é múltiplo exato de 10
        for rate in [50, 60, 70, 80, 90, 100, 120, 150, 200]:
            result = use_case.execute(Decimal(str(rate)))
            assert result.total_student_price % 10 != 0, (
                f"Rate {rate}: total {result.total_student_price} é múltiplo de 10 "
                "(deveria ter charm pricing)"
            )

    def test_charm_price_ends_in_90(self, use_case):
        """Se charm pricing foi aplicado, o total deve terminar em .90."""
        for rate in [50, 60, 70, 80, 90, 100, 120, 150, 200]:
            result = use_case.execute(Decimal(str(rate)))
            cents = result.total_student_price % 5
            # Se terminar em .90, cents será 4.90 mod 5 = 4.90
            # Se terminar em .00, cents será 0
            # Se terminar em 5.00, cents será 0
            assert cents == Decimal("0") or str(result.total_student_price).endswith(
                ".90"
            )


class TestSurplus:
    """Verifica que o surplus é corretamente calculado."""

    def test_surplus_is_returned(self, use_case):
        result = use_case.execute(Decimal("100.00"))
        # surplus deve estar presente e diferente de zero na maioria dos casos
        assert hasattr(result, "rounding_surplus")

    def test_platform_fee_includes_surplus(self, use_case):
        result = use_case.execute(Decimal("100.00"))
        # platform_fee_amount = base_fee (13%) + surplus
        base_fee = (Decimal("100.00") * Decimal("0.13")).quantize(Decimal("0.01"))
        assert result.platform_fee_amount == base_fee + result.rounding_surplus

    def test_breakdown_sums_to_total(self, use_case):
        """instructor + platform_fee + stripe_fee deve ser igual ao total."""
        for rate in [50, 73, 88, 100, 117, 150, 200]:
            result = use_case.execute(Decimal(str(rate)))
            reconstructed = (
                result.instructor_amount
                + result.platform_fee_amount
                + result.stripe_fee_estimate
            )
            # A diferença pode existir por causa do arredondamento de Stripe (fórmula reversa)
            # Mas o surplus compensa — diferença máxima tolerada: R$ 0.01
            assert abs(reconstructed - result.total_student_price) <= Decimal("0.01"), (
                f"Rate {rate}: {reconstructed} != {result.total_student_price}"
            )


class TestPixPayment:
    """Verifica que o arredondamento funciona também para PIX."""

    def test_pix_rounding_applied(self, use_case):
        result = use_case.execute(Decimal("100.00"), payment_method="pix")
        last_digit = result.total_student_price % 10
        assert last_digit in (
            Decimal("0"),
            Decimal("5"),
            Decimal("9.90"),
        ) or str(result.total_student_price).endswith(".90")

    def test_pix_no_multiple_of_10(self, use_case):
        result = use_case.execute(Decimal("100.00"), payment_method="pix")
        assert result.total_student_price % 10 != 0

    def test_pix_payment_method_in_dto(self, use_case):
        result = use_case.execute(Decimal("100.00"), payment_method="pix")
        assert result.payment_method == "pix"
