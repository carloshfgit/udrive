# Fluxo de Pagamento e Agendamento - GoDrive

Este documento detalha o fluxo completo de compra, agendamento, repasse e cancelamento de aulas na plataforma GoDrive.

## 1. Fluxo de Compra (Aluno)

1.  **Seleção e Agendamento:** O aluno seleciona o instrutor e escolhe os horários disponíveis nas telas de agendamento.
2.  **Carrinho:** As aulas selecionadas são enviadas para o carrinho. 
    *   *Reserva Temporária:* Ao iniciar o checkout, os horários ficam bloqueados temporariamente (ex: 15 min) para evitar conflitos de reserva simultânea.
3.  **Checkout:** O aluno realiza o pagamento na tela de checkout utilizando o formulário integrado do Stripe (Cartão de Crédito ou PIX).
4.  **Confirmação:** Após a confirmação do pagamento:
    *   As aulas são migradas para as telas de agenda (Aluno e Instrutor).
    *   O chat entre aluno e instrutor é desbloqueado para combinação de detalhes.
    *   O valor total fica retido sob custódia da plataforma no Stripe.

## 2. Fluxo de Conclusão e Repasse (Instrutor)

O GoDrive utiliza um modelo de custódia (escrow) para garantir a segurança da transação. Search & Transfers (ou Separate Charges and Transfers) do Stripe Connect.

1.  **Confirmação Manual:** Após o término da aula, o aluno confirma a conclusão no aplicativo.
    *   O repasse é acionado imediatamente para a conta Connect do instrutor (Split automático).
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

## 5. Observações Fiscais e Operacionais (Stripe Connect)

*   **Split de Pagamento:** O sistema utiliza o Stripe Connect para realizar o split (divisão) de valores. A plataforma recebe apenas a comissão de intermediação.
*   **Tributação:** O modelo de split garante que a plataforma seja tributada apenas sobre o valor da sua taxa, e não sobre o valor total da aula, evitando a bitributação.
*   **Retenção de Taxas:** Em casos de reembolso, as taxas de transação do Stripe podem ser retidas dependendo da configuração financeira da plataforma.

## 6. Modelo de Precificação e Taxas

Para garantir a transparência e a previsibilidade financeira dos instrutores, o GoDrive adota um modelo onde o **aluno paga todas as taxas e comissões**.

*   **Composição do Valor Final:** O valor pago pelo aluno é composto pelo:
    1.  **Valor da Aula:** Definido pelo instrutor em seu perfil.
    2.  **Comissão da Plataforma:** 20% calculado sobre o valor da aula.
    3.  **Taxas de Transação:** Taxas cobradas pelo Stripe para processamento do pagamento.
*   **Repasse ao Instrutor:** O instrutor recebe o valor integral ("limpo") que definiu. 
    *   *Exemplo:* Se o instrutor define o valor da aula em **R$ 80,00**, ele receberá exatamente **R$ 80,00**.
*   **Exemplo de Fluxo Financeiro (Base R$ 80,00):**
    *   Valor do Instrutor: R$ 80,00
    *   Comissão GoDrive (20%): R$ 16,00
    *   Estimativa de Taxas Stripe: ~ R$ 4,00
    *   **Valor Final para o Aluno: ~ R$ 100,00**
*   **Exibição de Preços (Transparência):**
    *   **Telas de Busca e Agendamento (Visão Aluno):** O valor exibido já é o **valor FINAL** (Preço Base + Comissão + Taxas). Isso garante que o aluno não tenha surpresas no checkout.
    *   **Edição de Perfil e Agenda (Visão Instrutor):** O instrutor vê e define o valor que ele efetivamente receberá por aula.

