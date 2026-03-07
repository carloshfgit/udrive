# REFUNDS_REFACTOR — Plano de Refatoração de Reembolsos Seletivos

> **Objetivo:** Permitir que o admin reembolse apenas 1 (ou N < total) aulas dentro de um checkout multi-item,
> mantendo as demais aulas com status `COMPLETED` e seus agendamentos ativos.

---

## Contexto do Problema

Hoje o sistema trata o pagamento do MP como um bloco único. Quando chega um webhook de `refunded`
ou `charged_back`, o handler em `HandlePaymentWebhookUseCase._handle_refunded()` marca **todos**
os `Payment` do grupo (`preference_group_id`) como `REFUNDED` — sem distinção de qual aula
foi de fato reembolsada.

O Mercado Pago **não tem conceito de item-level refund**: ele apenas reembolsa um `amount` do
pagamento total. A lógica de "qual aula foi reembolsada" é inteiramente responsabilidade do
sistema `udrive`.

---

## Visão Geral das Fases

```
FASE 1 — Banco de Dados
   └── Novo campo: payments.mp_refund_id

FASE 2 — Domínio e Gateway
   └── Entidade Payment + IPaymentGateway: suporte a reembolso parcial com retorno do refund_id

FASE 3 — Caso de Uso: iniciar reembolso seletivo
   └── Novo use case: RefundSinglePaymentUseCase

FASE 4 — Handler de Webhook: tratar `partially_refunded`
   └── Atualizar HandlePaymentWebhookUseCase para mapeamento por refund_id

FASE 5 — Integração com Disputas
   └── Atualizar ResolveDisputeUseCase para disparar RefundSinglePaymentUseCase

FASE 6 — Admin Panel (Next.js)
   └── UI para seleção de aulas a reembolsar

FASE 7 — Testes
   └── Unit + integração cobrindo os novos fluxos
```

---

## FASE 1 — Banco de Dados

**Arquivo-alvo:** `infrastructure/db/models/payment_model.py` + nova migração Alembic

### O que fazer

Adicionar o campo `mp_refund_id` ao model `PaymentModel`:

```python
mp_refund_id: Mapped[str | None] = mapped_column(nullable=True, index=True)
```

Este campo armazena o ID do reembolso retornado pelo MP (`refunds[].id`), vinculando
um `Payment` interno a um reembolso específico no gateway.

### Estratégia

- Gerar migração Alembic normalmente.
- Campo nullable → sem impacto em dados existentes.
- Adicionar também na entidade `Payment` e no `to_entity` / `from_entity`.

---

## FASE 2 — Domínio e Gateway

**Arquivos-alvo:**
- `domain/entities/payment.py`
- `domain/interfaces/payment_gateway.py`
- `infrastructure/external/mercadopago_gateway.py`

### O que fazer

1. **Entidade `Payment`:** adicionar campo `mp_refund_id: str | None = None`.

2. **`IPaymentGateway`:** adicionar método:
   ```python
   async def create_refund(
       self, mp_payment_id: str, amount: Decimal, access_token: str
   ) -> str:  # retorna o refund_id do MP
       ...
   ```

3. **`MercadoPagoGateway`:** implementar `create_refund()` chamando:
   ```
   POST /v1/payments/{mp_payment_id}/refunds
   Body: { "amount": <valor_da_aula> }
   ```
   Retornar `response["id"]` (o `refund_id`).

4. **`IPaymentGateway`:** adicionar também:
   ```python
   async def get_refunds(
       self, mp_payment_id: str, access_token: str
   ) -> list[dict]:  # lista de refunds do MP
       ...
   ```
   Útil no webhook para cruzar `refund_id` com `Payment.mp_refund_id`.

---

## FASE 3 — Caso de Uso: Iniciar Reembolso Seletivo

**Arquivo-alvo:** novo `application/use_cases/payment/refund_single_payment.py`

### O que fazer

Criar `RefundSinglePaymentUseCase` com o seguinte fluxo:

```
1. Recebe: payment_id (interno), admin_id
2. Busca Payment no repositório
3. Valida: status == COMPLETED, não tem mp_refund_id ainda
4. Busca instrutor → acessa token MP
5. Chama gateway.create_refund(mp_payment_id, payment.amount, token)
   → recebe refund_id do MP
6. Atualiza payment:
   - mp_refund_id = refund_id
   - status = PARTIALLY_REFUNDED (ou REFUNDED se for 100%)
   - refund_amount = payment.amount
   - refunded_at = now()
7. Persiste payment
8. Cria Transaction de reembolso (crédito para aluno)
9. Atualiza Scheduling → CANCELLED (ou outro status adequado)
```

### Por que agir diretamente (sem esperar webhook)?

Ao chamar a API do MP para criar o reembolso, o sistema já recebe confirmação imediata.
O webhook que chegar depois deve ser **idempotente** (sistema já estará no estado correto).

---

## FASE 4 — Handler de Webhook: `partially_refunded`

**Arquivo-alvo:** `application/use_cases/payment/handle_payment_webhook.py`

### O que fazer

1. **Adicionar `"partially_refunded"` ao `MP_STATUS_MAP`** → mas **não** mapeá-lo diretamente para um `PaymentStatus`.
   Em vez disso, detectar explicitamente via `status_detail`.

2. **Nova lógica em `_process_single_payment`:**
   ```
   se status_result.status == "approved" e status_detail == "partially_refunded":
       → chamar _handle_partial_refund(payment, status_result)
   ```

3. **Novo método `_handle_partial_refund`:**
   ```
   1. Buscar refunds do MP via gateway.get_refunds(mp_payment_id)
   2. Para cada refund:
      - Checar se algum Payment do grupo tem mp_refund_id == refund["id"]
      - Se sim → idempotente, ignorar
      - Se não → encontrar o Payment pelo valor (fallback) e associar
   3. Atualizar apenas os Payments afetados
   ```

4. **Não alterar a lógica de `_handle_refunded`** (status `refunded` = reembolso total)
   — esse caminho continua marcando todos do grupo.

### Sobre o `charged_back` (disputa via painel MP)

O `charged_back` sempre indica reembolso total pelo banco. Pode continuar mapeando
para `REFUNDED` e atingindo todo o grupo. Caso o valor do `charged_back` seja parcial,
o comportamento de `_handle_partial_refund` acima cobrirá isso via `status_detail`.

---

## FASE 5 — Integração com Disputas

**Arquivo-alvo:** `application/use_cases/scheduling/resolve_dispute.py`

### O que fazer

Quando a resolução é `FAVOR_STUDENT`, o use case hoje apenas muda o estado do
scheduling. O reembolso real é disparado fora (Celery task). Com a refatoração:

1. **`ResolveDisputeDTO`** deve incluir:
   - `payment_ids_to_refund: list[UUID]` — lista dos `Payment` internos a serem reembolsados
   - (pode ser 1, alguns ou todos do grupo)

2. **`ResolveDisputeUseCase`** deve:
   - Delegar para `RefundSinglePaymentUseCase` para cada `payment_id` da lista
   - Atualizar apenas os Schedulings correspondentes para `CANCELLED`
   - Deixar os demais Schedulings do grupo em `COMPLETED`

3. **Admin panel** passa a lista de `payment_ids` selecionados pelo admin
   ao confirmar a resolução a favor do aluno.

---

## FASE 6 — Admin Panel (Next.js)

**Diretório-alvo:** `admin/`

### O que fazer

Na página de detalhes de uma disputa (`/disputes/[id]`):

1. **Listar as aulas do checkout** — buscar todos os `Payment` do `preference_group_id`
   via novo endpoint: `GET /admin/disputes/{id}/payments`

2. **Seleção interativa** — checkboxes para o admin marcar quais aulas reembolsar

3. **Enviar ao resolver** — ao clicar em "Resolver a favor do aluno", enviar
   o array de `payment_ids` selecionados no body da requisição

4. **Exibir status** — mostrar para cada aula se está `COMPLETED`, `REFUNDED` ou `PARTIALLY_REFUNDED`

---

## FASE 7 — Testes

Todos os testes devem rodar dentro do Docker (conforme regra do projeto).

### Cobertura obrigatória

| Cenário | Tipo de teste |
|---|---|
| `create_refund` retorna `refund_id` válido | Unit (mock gateway) |
| `RefundSinglePaymentUseCase` associa `mp_refund_id` ao Payment correto | Unit |
| Webhook `partially_refunded` atualiza apenas 1 de 4 Payments | Unit |
| Webhook `refunded` (total) atualiza todos do grupo | Unit (regressão) |
| `ResolveDisputeUseCase` com lista parcial de payment_ids | Unit |
| Fluxo completo: admin seleciona 1 aula → reembolso MP → webhook idempotente | Integração |

---

## Dependências entre Fases

```
FASE 1 → FASE 2 → FASE 3 → FASE 5
                         ↓
                      FASE 4  (pode ser paralela ao 3)
                         ↓
                      FASE 6  (depende do 3 e 5)
                         ↓
                      FASE 7  (depende de tudo)
```

> **Recomendação:** Implementar FASE 1–3 juntas (são backend puro, sem visual),
> depois FASE 4 (webhook), depois FASE 5 (disputas) e por fim FASE 6 (UI) com cobertura de testes ao longo de cada fase.
