import math
from decimal import Decimal, ROUND_CEILING

def calcular_precificacao():
    print("=== Calculadora de Precificação GoDrive ===")
    
    try:
        # Inputs do usuário
        valor_instrutor = Decimal(input("Valor que o instrutor quer receber (R$): ").replace(',', '.'))
        taxa_godrive_perc = Decimal(input("Taxa GoDrive (%): ").replace(',', '.'))
        
        # Taxa Mercado Pago fixa conforme pedido
        taxa_mp_perc = Decimal("4.98")
        
        # 1. Converter taxas para decimal
        platform_fee = taxa_godrive_perc / Decimal("100")
        mp_fee = taxa_mp_perc / Decimal("100")
        
        # 2. Cálculo do Subtotal (Base + GoDrive Fee) / (1 - MP Fee)
        target_net = valor_instrutor * (Decimal("1.0") + platform_fee)
        divisor = Decimal("1.0") - mp_fee
        
        if divisor <= 0:
            subtotal = target_net
        else:
            subtotal = target_net / divisor
        
        # 3. Arredondamento para o próximo múltiplo de 5 acima
        multiplier = Decimal("5.0")
        rounded = (subtotal / multiplier).quantize(Decimal("1"), rounding=ROUND_CEILING) * multiplier
        
        # 4. Charm Pricing: Se o valor arredondado terminar em zero, subtraímos 0.10
        if rounded % Decimal("10.0") == 0:
            valor_final_aluno = rounded - Decimal("0.10")
        else:
            valor_final_aluno = rounded
            
        valor_final_aluno = valor_final_aluno.quantize(Decimal("0.01"))
        
        # 5. Cálculo dos Repasses
        # O MP cobra sua taxa sobre o valor TOTAL pago pelo aluno
        valor_mp = (valor_final_aluno * mp_fee).quantize(Decimal("0.01"))
        
        # O que sobra depois da taxa do MP
        valor_pos_mp = valor_final_aluno * (Decimal("1.0") - mp_fee)
        
        # O que o GoDrive recebe é o que sobra após pagar o instrutor e o MP
        valor_godrive = (valor_pos_mp - valor_instrutor).quantize(Decimal("0.01"))
        
        # Resultados
        print("\n" + "="*40)
        print(f"VALOR QUE O ALUNO VERÁ:       R$ {valor_final_aluno:>8}")
        print(f"VALOR QUE O GODRIVE RECEBERÁ: R$ {valor_godrive:>8}")
        print(f"VALOR QUE O MP RECEBERÁ:      R$ {valor_mp:>8}")
        print(f"VALOR QUE O INSTRUTOR RECEBE: R$ {valor_instrutor:>8}")
        print("="*40)
        
    except Exception as e:
        print(f"\nErro nos dados informados: {e}")

if __name__ == "__main__":
    calcular_precificacao()
