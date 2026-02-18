from decimal import Decimal
import pytest
from src.infrastructure.services.pricing_service import PricingService

def test_calculate_final_price():
    # Exemplos da documentação:
    
    # 1. R$ 65,00 -> Subtotal R$ 81,25 (estimado) -> Arredondamento R$ 85,00 -> Final R$ 85,00 (mantido, termina em 5)
    # Cálculo manual: 65 * (1 + 0.20 + 0.0498) = 65 * 1.2498 = 81.237 -> ceil(81.237/5)*5 = 85 -> R$ 85.00
    assert PricingService.calculate_final_price(Decimal("65.00")) == Decimal("85.00")
    
    # 2. R$ 70,00 -> Subtotal R$ 87,50 (estimado) -> Arredondamento R$ 90,00 -> Final R$ 89,90
    # Cálculo manual: 70 * 1.2498 = 87.486 -> ceil(87.486/5)*5 = 90 -> Charm Pricing -> R$ 89.90
    assert PricingService.calculate_final_price(Decimal("70.00")) == Decimal("89.90")
    
    # 3. R$ 80,00 -> Subtotal R$ 100,00 (estimado) -> Arredondamento R$ 100,00 -> Final R$ 99,90
    # Cálculo manual: 80 * 1.2498 = 99.984 -> ceil(99.984/5)*5 = 100 -> Charm Pricing -> R$ 99.90
    assert PricingService.calculate_final_price(Decimal("80.00")) == Decimal("99.90")

def test_calculate_marketplace_fee():
    # Verificar se o instrutor recebe o valor base após as taxas
    # Ex: final_price 85.00, base 65.00
    # MP Fee (4.98%) = 85.00 * 0.0498 = 4.233
    # marketplace_fee = (85.00 * 0.9502) - 65.00 = 80.767 - 65.00 = 15.767 -> 15.77
    fee = PricingService.calculate_marketplace_fee(Decimal("85.00"), Decimal("65.00"))
    assert fee == Decimal("15.77")
    
    # Verificação: 85.00 - 4.23 (taxa MP) - 15.77 (marketplace_fee) = 65.00 (Valor para o vendedor)
    # 85.00 - 4.233... = 80.767
    # 80.767 - 15.77 = 64.997 -> ~ 65.00
    
    # Ex: final_price 89.90, base 70.00
    # After MP Tax = 89.90 * 0.9502 = 85.42298
    # fee = 85.42298 - 70.00 = 15.42298 -> 15.42
    fee2 = PricingService.calculate_marketplace_fee(Decimal("89.90"), Decimal("70.00"))
    assert fee2 == Decimal("15.42")
