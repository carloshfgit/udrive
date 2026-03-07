# Sistema de Reembolsos — GoDrive

Este documento detalha o funcionamento técnico e as regras de negócio do sistema de reembolsos da GoDrive, bem como sua integração com o Mercado Pago.

## 1. Arquitetura de Pagamentos

O sistema utiliza um modelo de **checkout multi-item**. Embora o aluno realize um único pagamento no Mercado Pago, internamente o sistema gerencia as aulas de forma individualizada.

- **Preference Group**: Múltiplos agendamentos (`Scheduling`) são agrupados sob um `preference_group_id`.
- **Payments Individuais**: Cada aula possui seu próprio registro na entidade `Payment`.
- **Gateway ID**: Todos os `Payments` de um mesmo checkout compartilham o mesmo `gateway_payment_id` do Mercado Pago.
- **Vantagem**: Isso permite reembolsar apenas uma aula específica de um pacote de cinco, sem afetar as demais.

---

## 2. Regras de Reembolso Automático

Quando um aluno ou instrutor cancela uma aula, o sistema aplica regras automáticas baseadas na antecedência do cancelamento em relação ao horário da aula.

| Antecedência | % Reembolso Aluno | Observação |
| :--- | :--- | :--- |
| **> 48 horas** | 100% | Reembolso integral. |
| **24 a 48 horas** | 50% | 50% é retido como taxa de reserva para o instrutor. |
| **< 24 horas** | 0% | Nenhum valor é devolvido ao aluno. |
| **Cancelamento pelo Instrutor** | 100% | O aluno sempre recebe 100% se o instrutor cancelar. |

### Trava de Reagendamento
Se uma aula for reagendada dentro da janela de multa (< 48h), o sistema preserva a data original em `original_scheduled_datetime`. Caso essa aula seja cancelada posteriormente, a multa será calculada com base na data original, impedindo que o aluno use o reagendamento para "resetar" o timer de reembolso.

---

## 3. Disputas e Reembolsos Seletivos

Através do Painel Administrativo, é possível resolver disputas com reembolsos manuais.

- **Reembolso Parcial vs Total**: O administrador pode escolher entre reembolso integral (100%) ou parcial (50% por padrão).
- **Seleção de Pagamentos**: Em disputas de pacotes, o administrador pode selecionar especificamente quais `payment_ids` devem ser reembolsados.
- **Efeito no Scheduling**: Ao reembolsar um pagamento via disputa, o agendamento associado é automaticamente movido para o status `CANCELLED`.

---

## 4. Integração com Mercado Pago

### Checkout Pro
O sistema utiliza o Checkout Pro (Redirecionamento). 
- O gateway recebe uma lista de `items`, onde cada item corresponde a uma aula.
- O `external_reference` da preferência no MP é preenchido com o `preference_group_id`.

### Processamento de Reembolso (API de Refunds)
O sistema utiliza a API de Reembolsos do Mercado Pago (`POST /v1/payments/{payment_id}/refunds`).
- O reembolso é sempre disparado de forma parcial em relação ao pagamento total do MP, usando o valor exato da aula (`payment.amount`).
- **Token do Instrutor**: Como o sistema utiliza o modelo de Marketplace, o reembolso é disparado utilizando o `access_token` do instrutor (vendedor), garantindo que o valor saia diretamente da conta dele.

### Webhooks e Sincronização
O sistema processa webhooks do tipo `payment.updated`.
- **Detecção de Reembolso Parcial**: Quando o MP notifica um reembolso parcial, o `HandlePaymentWebhookUseCase` consulta a API de de refunds do MP e tenta associar o evento ao `Payment` correto no banco de dados.
- **Match por Valor**: Caso não haja um vínculo direto (via `mp_refund_id`), o sistema tenta encontrar o `Payment` correspondente pelo valor exato reembolsado.

---

## 5. Fluxo Técnico de Execução

1. **Pedido de Cancelamento**: Ocorre via app Mobile ou Painel Admin.
2. **Cálculo Domain**: A entidade `Scheduling` calcula o percentual de direito.
3. **Persistência**: O status do agendamento muda para `CANCELLED`.
4. **Task Assíncrona**: Uma task Celery (`process_refund_task`) é disparada para evitar travamentos em caso de lentidão da API do Mercado Pago.
5. **Chamada Gateway**: O backend descriptografa o token do instrutor e solicita o reembolso ao MP.
6. **Confirmação**: O `mp_refund_id` retornado pelo MP é salvo no banco para garantir idempotência.

---

## 6. Logs e Auditoria
Cada reembolso gera uma transação no sistema (`Transaction`) do tipo `REFUND`, permitindo rastrear o fluxo financeiro para conciliação bancária.
