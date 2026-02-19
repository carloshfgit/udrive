# Fluxo de Pagamento e Agendamento - GoDrive

Este documento detalha o fluxo completo de compra, agendamento, repasse e cancelamento de aulas na plataforma GoDrive.

## 1. Fluxo de Compra (Aluno)

1.  **Seleção e Agendamento:** O aluno seleciona o instrutor e escolhe os horários disponíveis nas telas de agendamento.
2.  **Carrinho:** As aulas selecionadas são enviadas para o carrinho. 
    *   *Reserva Temporária:* Ao iniciar o checkout, os horários ficam bloqueados temporariamente (12 min) para evitar conflitos de reserva simultânea.
3.  **Checkout:** O aluno realiza o pagamento via **Mercado Pago Checkout Pro** (Cartão de Crédito, PIX ou saldo Mercado Pago).
4.  **Confirmação:** Após a confirmação do pagamento:
    *   As aulas são migradas para as telas de agenda (Aluno e Instrutor).
    *   O chat entre aluno e instrutor é desbloqueado para combinação de detalhes.
    *   O valor total fica retido sob custódia da plataforma no **Mercado Pago**.

## 2. Fluxo de Conclusão e Repasse (Instrutor)

O GoDrive utiliza um modelo de custódia (escrow) para garantir a segurança da transação via **Mercado Pago Marketplace**.

1.  **Confirmação Manual:** Após o término da aula, o aluno confirma a conclusão no aplicativo.
    *   O repasse é acionado imediatamente para a conta Mercado Pago do instrutor (Split automático via Marketplace Fee).
2.  **Confirmação Automática (Gatilho de Segurança):** Caso o aluno esqueça de confirmar, o sistema realiza a confirmação automática **24 horas após o horário previsto de término** da aula, liberando o pagamento ao instrutor.
3.  **Disputa:** Se o aluno reportar um problema (ex: instrutor não apareceu) antes da confirmação automática, o repasse é bloqueado para análise manual do suporte.

## 3. Regras de Reagendamento

O reagendamento é uma ferramenta para flexibilidade, mas possui travas para evitar abusos na política de reembolso:

*   **Gratuidade:** Reagendamentos são sempre gratuitos.
*   **Solicitação:** Pode ser solicitado tanto por aluno quanto por instrutor. A aula só muda de horário após a aceitação da outra parte.
*   **Limitação:** Limite de 1 (um) reagendamento gratuito por aula para evitar ciclos infinitos de reserva.
*   **Impacto no Gatilho:** Ao aceitar um reagendamento, o gatilho de confirmação automática é resetado e ancorado na nova data/hora.
*   **Trava de Reembolso:** Uma aula reagendada dentro da janela de multa (menos de 48h para o início original) mantém sua "janela de multa original" para fins de cálculo de reembolso caso venha a ser cancelada posteriormente.

## 4. Regras de Reembolso e Cancelamento

O percentual de reembolso é calculado com base na antecedência do cancelamento em relação ao início da aula:

| Antecedência | Percentual de Reembolso | Observação |
| :--- | :--- | :--- |
| **>= 48 horas** | 100% | Reembolso integral. |
| **Entre 24h e 48h** | 50% | Retenção de 50% como taxa de reserva para o instrutor. |
| **< 24 horas** | 0% | Sem direito a reembolso (pagamento integral ao instrutor). |
| **Emergência** | 100% | Reembolso integral mediante justificativa e aprovação do suporte. |

## 5. Observações Fiscais e Operacionais (Mercado Pago Marketplace)

*   **Split de Pagamento:** O sistema utiliza o **Mercado Pago Marketplace** para realizar o split (divisão) de valores. A plataforma recebe apenas a comissão de intermediação (Marketplace Fee).
*   **Tributação:** O modelo de split garante que a plataforma seja tributada apenas sobre o valor da sua taxa, e não sobre o valor total da aula, evitando a bitributação.
*   **Retenção de Taxas:** Em casos de reembolso, as taxas de transação do Mercado Pago podem ser retidas dependendo da configuração financeira da plataforma.

## 6. Tabela de Taxas (Brasil)

Taxas vigentes para recebimento no momento (Checkout Pro):

| Meio de Pagamento | Taxa (%) / Valor | Dinheiro Disponível |
| :--- | :--- | :--- |
| **Cartão de Crédito** | 4,98% | Na hora* |
| | 4,49% | 14 dias |
| | 3,98% | 30 dias |
| **Pix** | 0,99% | Na hora |
| **Saldo Mercado Pago** | 4,99% | Na hora |
| **Boleto** | R$ 3,49 | 1 a 2 dias úteis |

## 7. Modelo de Precificação e Taxas

O GoDrive adota um modelo "fee-on-top" modificado (Markup), onde o **cálculo garante que o instrutor receba o valor integral** ("limpo") definido em seu perfil, considerando que a taxa do Mercado Pago incide sobre o valor total da transação. Além disso, aplicamos regras de arredondamento e precificação psicológica.

*   **Composição do Valor Final:** O cálculo segue a ordem abaixo:
    1.  **Valor Base:** Definido pelo instrutor.
    2.  **Target Líquido:** Base + 20% (Comissão GoDrive).
    3.  **Markup Mercado Pago:** O valor é dividido por `(1 - Taxa MP)` para embutir a taxa do meio de pagamento.
    4.  **Arredondamento:** O subtotal é arredondado para o **próximo múltiplo de 5 acima**.
    5.  **Charm Pricing:** Se terminar em 0, subtrai R$ 0,10.

*   **Monetização e Repasse:** 
    *   **Plataforma:** Recebe sua comissão de 20% + excedentes do arredondamento.
    *   **Instrutor:** Recebe exatamente o valor base contratado.

*   **Exemplos Práticos:**

| Valor Instrutor | Cálculo Markup (Base + 20%) / (1 - 4.98%) | Arredondamento | Valor Final |
| :--- | :--- | :--- | :--- |
| **R$ 65,00** | R$ 82,09 (Target 78 / 0.9502) | R$ 85,00 | **R$ 85,00** |
| **R$ 70,00** | R$ 88,40 (Target 84 / 0.9502) | R$ 90,00 | **R$ 89,90** |
| **R$ 100,00** | R$ 126,29 (Target 120 / 0.9502) | R$ 130,00 | **R$ 129,90** |

*   **Exibição de Preços (Transparência):**
    *   **Visão Aluno:** O valor exibido nas telas de busca e agendamento já é o **Valor Final** (com todas as taxas, arredondamentos e charm pricing aplicados).
    *   **Visão Instrutor:** O instrutor define e visualiza o valor líquido de sua hora-aula.


