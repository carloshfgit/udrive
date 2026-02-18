
import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from src.infrastructure.services.pricing_service import PricingService
from src.infrastructure.config import settings

# Mock settings for predictable tests
@pytest.fixture
def mock_settings():
    with patch("src.infrastructure.services.pricing_service.settings") as mock:
        mock.platform_fee_percentage = 20.0
        mock.mercadopago_fee_percentage = 4.98
        yield mock

class TestPricingService:

    def test_calculate_final_price_logic_markup(self, mock_settings):
        """
        Verifica se a logica de markup garante o valor líquido do instrutor.
        Cenário: Instrutor quer R$ 100.00
        Platform Fee: 20% -> Target Net = 120.00
        MP Fee: 4.98% (Divisor = 0.9502)
        Price Needed = 120.00 / 0.9502 = 126.289...
        Round up to next 5 -> 130.00
        Charm Price -> 129.90 (pois 130 termina em 0)
        """
        base_price = Decimal("100.00")
        final_price = PricingService.calculate_final_price(base_price)
        
        # Esperado: 129.90
        assert final_price == Decimal("129.90")

    def test_calculate_final_price_low_value(self, mock_settings):
        """
        Cenário: Instrutor quer R$ 65.00
        Target Net = 65 * 1.2 = 78.00
        Price Needed = 78.00 / 0.9502 = 82.087...
        Round up to 5 -> 85.00
        Charm Price -> 85.00 (termina em 5, nao aplica)
        """
        base_price = Decimal("65.00")
        final_price = PricingService.calculate_final_price(base_price)
        
        assert final_price == Decimal("85.00")

    def test_calculate_final_price_charm_pricing(self, mock_settings):
        # Teste específico para quando o arredondamento cai em múltiplo de 10
        # Ex: Resultado arredondado = 90.00 -> deve virar 89.90
        
        # Reverse engineering de um caso que dê 90.00
        # 90 * 0.9502 = 85.518 (price needed)
        # 85.518 / 1.2 = 71.265 (base price)
        
        base_price = Decimal("71.27") 
        final_price = PricingService.calculate_final_price(base_price)
        # 71.27 * 1.2 = 85.524
        # 85.524 / 0.9502 = 90.006 -> round to 95.00 (Wait, logic check)
        
        # Vamos usar um valor exato calculado manualmente
        # Base 70.00
        # Target = 84.00
        # Needed = 84 / 0.9502 = 88.40
        # Round 5 -> 90.00
        # Charm -> 89.90
        
        base_price = Decimal("70.00")
        final_price = PricingService.calculate_final_price(base_price)
        assert final_price == Decimal("89.90")

    def test_calculate_marketplace_fee_integrity(self, mock_settings):
        """
        Garante que a marketplace_fee cobre o valor do instrutor e sobra para a plataforma.
        """
        base_price = Decimal("100.00")
        final_price = PricingService.calculate_final_price(base_price) # 129.90
        
        mp_fee = Decimal(str(mock_settings.mercadopago_fee_percentage)) / 100
        
        # Simula o desconto do MP
        valor_liquido_apos_mp = final_price * (1 - mp_fee)
        
        marketplace_fee = PricingService.calculate_marketplace_fee(final_price, base_price)
        
        # O que o MP vai pagar na conta do vendedor (split):
        valor_na_conta_vendedor_antes_split = valor_liquido_apos_mp
        # O split retira mp_fee
        saldo_vendedor = valor_na_conta_vendedor_antes_split - marketplace_fee
        
        # O saldo do vendedor deve ser >= base_price (pode ser maior por causa do arredondamento a favor dele ou da plataforma? 
        # Pela logica do split, o marketplace_fee eh calculado para deixar APENAS o base_price pro vendedor?
        # Vamos verificar a implementacao e calculate_marketplace_fee:
        # marketplace_fee = after_mp_tax - instructor_base_price
        # Logo: instructor_base_price = after_mp_tax - marketplace_fee
        
        # Assert matemático da fórmula
        assert abs(saldo_vendedor - base_price) < Decimal("0.02") # Tolerancia de centavos

    def test_zero_price(self, mock_settings):
        assert PricingService.calculate_final_price(Decimal("0")) == Decimal("0.00")
        assert PricingService.calculate_final_price(Decimal("-10")) == Decimal("0.00")

