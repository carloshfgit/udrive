# Relatório: Mercado Pago para Marketplaces

## 1. Lógica de Reembolso (Checkout Pro com Split)

Quando uma venda é realizada via Checkout Pro com Split de Pagamento, o valor é dividido entre o Vendedor (Instrutor) e o Marketplace (Sua Plataforma) no momento do pagamento.

### Como funciona o estorno/reembolso:

- **Proporcionalidade:** Ao realizar um reembolso (total ou parcial) para o comprador, o Mercado Pago retira os fundos de ambas as contas envolvidas (Vendedor e Marketplace) na mesma proporção em que foram creditados.
- **Taxas do Mercado Pago:** O Mercado Pago devolve ("estorna") a taxa de processamento original da transação. Ou seja, a plataforma não "perde" a taxa do gateway no caso de um reembolso total; o valor integral volta para o comprador.
- **Comissão da Plataforma (Marketplace Fee):** A comissão que sua plataforma recebeu também é estornada (total ou parcialmente) para compor o valor devolvido ao comprador.
- **Saldo Insuficiente:** Se o vendedor (instrutor) não tiver saldo suficiente na conta do Mercado Pago para cobrir a parte dele do reembolso, o reembolso pode falhar ou o Mercado Pago pode tentar retirar de cartões cadastrados/ficar com saldo negativo (dependendo da configuração e análise de risco da conta do vendedor). **Ponto de Atenção:** É importante garantir que seus instrutores tenham saldo ou que a política de cancelamento da plataforma esteja alinhada com isso.

## 2. Prazos de Recebimento (Liberação dos Fundos)

O momento em que o dinheiro fica "Disponível" para uso (saque ou novas transações) depende da configuração de tarifa escolhida na conta.

### Para o Vendedor (Instrutor):

O prazo segue a configuração da conta do vendedor ou a regra imposta pelo marketplace na transação. As opções padrões são:

- **D+0 (Na hora):** Dinheiro disponível imediatamente após a aprovação do pagamento. (Taxas mais altas).
- **D+14 (14 dias):** Dinheiro disponível em 14 dias corridos. (Taxa padrão/intermediária).
- **D+30 (30 dias):** Dinheiro disponível em 30 dias corridos. (Taxas menores).

**No modelo de Marketplace:** Geralmente, a configuração de recebimento que vale é a da conta do vendedor (o "dono" principal dos fundos recebidos), a menos que o Marketplace force uma configuração específica via API na criação da preferência.

### Para a Plataforma (Marketplace):

A sua comissão (`marketplace_fee`) geralmente acompanha o prazo de liquidação da transação principal para garantir segurança contra chargebacks e fraudes.

- Se a transação for D+14, sua comissão também ficará disponível em D+14.
- Isso serve para proteger o ecossistema: se houver um chargeback (cancelamento pelo cartão) antes dos 14 dias, os fundos nem chegam a ser liberados.

## 3. Disponibilidade para Saque

Uma vez que o status do dinheiro muda de "A liberar" (ou "Bloqueado") para **"Disponível"**:

- **Transferência:** O saldo pode ser transferido para conta bancária, usado para pagar boletos ou transferido via Pix.
- **Prazos de Saque:**
    - **Pix:** Geralmente instantâneo (24/7).
    - **TED:** No mesmo dia se solicitado até determinado horário (geralmente 17h), ou no próximo dia útil.

## 4. Garantia de Reembolso Pré-Liquidação (Antes de D+14/D+30)

Se o aluno solicitar reembolso **antes** do prazo de liberação do dinheiro (enquanto está "A liberar"):

- **Financeiramente:** O dinheiro **está lá**. Como o vendedor ainda não sacou (pois está bloqueado), os fundos existem tecnicamente na conta para cobrir o estorno.
- **Operacionalmente (Risco):** A documentação do Mercado Pago informa que é necessário ter **"Dinheiro disponível"** ou **"Saldo suficiente"** para efetuar devoluções.
    - Isso cria um possível cenário de travamento: se o instrutor tiver R$ 0,00 de _Saldo Disponível_ (porque sacou tudo de vendas anteriores) e tiver apenas o _Saldo a Liberar_ da venda atual, o sistema **pode** impedir o reembolso automático alegando "saldo insuficiente", exigindo que o vendedor adicione dinheiro à conta.
    - **Mitigação:** No entanto, para cancelamentos feitos no mesmo dia (antes do processamento noturno) ou estornos diretos na transação, o sistema muitas vezes consegue apenas "cancelar" a entrada futura.
- **Conclusão:** O reembolso é **muito provável**, mas não 100% "garantido" via API se depender da verificação de saldo _disponível_ da conta do vendedor. O Vendedor (Instrutor) é o responsável final perante o Mercado Pago.

## 5. Viabilidade do Fluxo "Autorização e Captura" no Checkout Pro

**Não é viável com Checkout Pro para essa finalidade.**

### O que a pesquisa confirmou:

1. **Exclusividade do Checkout Transparente (API):** O fluxo de "Autorização e Captura" (Two-step payment), onde você reserva o limite e captura depois (em até 5 dias), é uma funcionalidade desenhada para o **Checkout Transparente** (`capture: false` na API de Payments).
2. **Limitação do Checkout Pro:** O Checkout Pro (Redirect) é projetado para conversão imediata (Single-step). Ele realiza a autorização e a captura simultaneamente para garantir a venda. Não existem parâmetros na criação da Preferência (`/checkout/preferences`) que permitam separar a autorização da captura.
3. **Comportamento do Split:** O Split de pagamento ocorre automaticamente no momento da liquidação/confirmação do pagamento. Tentar forçar uma lógica de "pré-autorização" com Checkout Pro não é suportado nativamente.

### Alternativas Recomendadas:

- **Usar o Prazo de Liberação (D+14):** A melhor forma de "segurar" o dinheiro no Checkout Pro é confiar no prazo de liberação (D+14 ou D+30). Durante esse período, o dinheiro está na conta do vendedor mas **bloqueado**. Se o aluno reclamar que não recebeu a aula, você (Plataforma) ou o Instrutor podem realizar o estorno antes que o dinheiro fique disponível para saque.
- **Migrar para Checkout Transparente:** Se a lógica de "reserva de limite" for crítica para o negócio (ex: evitar cobrar se o instrutor não confirmar a aula em 2h), seria necessário migrar do Checkout Pro para o **Checkout Transparente**, o que aumenta significativamente a complexidade de desenvolvimento (PCI compliance, gestão de frontend de pagamentos, gestão de risco pelo próprio marketplace).

## Resumo Executivo para Gestão

|Evento|O que acontece|
|---|---|
|**Venda Aprovada**|Dinheiro entra nas contas do Instrutor e Plataforma como "A liberar".|
|**Reembolso**|Valor é retirado proporcionalmente de ambas as contas. Taxas MP são estornadas.|
|**Reembolso Pré-Liquidação**|Dinheiro da venda ainda não saiu da conta, mas sistema pode exigir "saldo disponível" para operar o estorno.|
|**Liberação (D+X)**|Após X dias (ex: 14), o saldo vira "Disponível" para ambos.|
|**Saque**|Instrutor e Plataforma podem sacar via Pix/TED para seus bancos.|
