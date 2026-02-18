"""
Pricing Service

Implementa a lógica de precificação fee-on-top para o GoDrive.
- GoDrive Fee: configurável via PLATFORM_FEE_PERCENTAGE
- Mercado Pago Fee: configurável via MERCADOPAGO_FEE_PERCENTAGE
- Arredondamento: próximo múltiplo de 5
- Charm Pricing: -R$ 0,10 se terminar em 0
"""

from decimal import Decimal, ROUND_CEILING
import math
from src.infrastructure.config import settings

class PricingService:
    @staticmethod
    def calculate_final_price(base_price: Decimal) -> Decimal:
        """
        Calcula o preço final para o aluno com base no preço bruto do instrutor.
        
        Regras:
        1. Adicionar comissão GoDrive (configurável)
        2. Adicionar margem para taxa Mercado Pago (configurável)
        3. Arredondar para o próximo múltiplo de 5 acima
        4. Aplicar Charm Pricing (-0.10 se terminar em zero)
        """
        if base_price <= 0:
            return Decimal("0.00")

        # 1. Calcular Alvo Líquido (Base + GoDrive Fee)
        # target_net = base_price * (1 + platform_fee)
        platform_fee = Decimal(str(settings.platform_fee_percentage)) / Decimal("100")
        mp_fee = Decimal(str(settings.mercadopago_fee_percentage)) / Decimal("100")
        
        target_net = base_price * (Decimal("1.0") + platform_fee)

        # 2. Calcular Preço de Venda Necessário para cobrir taxa MP (Markup)
        # price_needed = target_net / (1 - mp_fee)
        # Se mp_fee for muito alto (ex: > 90%), isso quebraria. Assumimos taxas razoáveis.
        divisor = Decimal("1.0") - mp_fee
        if divisor <= 0:
            # Fallback de segurança para não dividir por zero ou negativo
            subtotal = target_net 
        else:
            subtotal = target_net / divisor
        
        # 3. Arredondar para o próximo múltiplo de 5 acima
        # rounded = ceil(subtotal / 5) * 5
        multiplier = Decimal("5.0")
        rounded = (subtotal / multiplier).quantize(Decimal("1"), rounding=ROUND_CEILING) * multiplier
        
        # 4. Charm Pricing: Se o valor arredondado terminar em zero (90, 100, etc), subtraímos 0.10
        # Simplificação: se for múltiplo de 10
        if rounded % Decimal("10.0") == 0:
            final_price = rounded - Decimal("0.10")
        else:
            final_price = rounded
            
        return final_price.quantize(Decimal("0.01"))

    @staticmethod
    def calculate_marketplace_fee(final_price: Decimal, instructor_base_price: Decimal) -> Decimal:
        """
        Calcula quanto de marketplace_fee a plataforma deve cobrar no Mercado Pago
        para garantir que o instrutor receba seu valor líquido.
        
        Fórmula: marketplace_fee = (final_price * (1 - MP_Taxa)) - instructor_base_price
        """
        mp_fee_rate = Decimal(str(settings.mercadopago_fee_percentage)) / Decimal("100")
        
        # O que sobra após a taxa do MP
        after_mp_tax = final_price * (Decimal("1.0") - mp_fee_rate)
        
        # A comissão da plataforma é o que sobra após pagar o instrutor
        marketplace_fee = after_mp_tax - instructor_base_price
        
        # Garantir que não seja negativo (pode ocorrer se as taxas mudarem drasticamente)
        return max(marketplace_fee, Decimal("0.00")).quantize(Decimal("0.01"))
