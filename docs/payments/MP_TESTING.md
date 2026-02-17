# Fluxo de Testagem Mercado Pago: Marketplace e Split de Pagamentos

Este documento descreve o fluxo de teste oficial para integrações de Marketplace com Split de Pagamentos, baseado na documentação oficial do Mercado Pago.

## 1. Tipos de Contas de Teste Necessárias

Para testar um fluxo de marketplace completo, o Mercado Pago recomenda a criação de pelo menos três tipos de contas no painel de desenvolvedor:

*   **Integrador (Marketplace):** A conta principal que gerencia a aplicação e recebe a comissão (`application_fee` ou `marketplace_fee`).
*   **Vendedor (Seller):** Conta que representa o vendedor final. Esta conta deve ser vinculada à aplicação do integrador via OAuth.
*   **Comprador (Buyer):** Conta utilizada para simular a compra e realizar o pagamento.

> [!IMPORTANT]
> As contas de **Vendedor** e **Comprador** devem pertencer ao mesmo país.

## 2. Configuração do Ambiente de Teste

1.  **Criação da Aplicação:** O Integrador deve criar uma aplicação no painel "Suas Integrações".
2.  **Fluxo OAuth (Vendedor):**
    *   O vendedor deve autorizar a aplicação do marketplace para operar em seu nome.
    *   Este processo resulta em um `access_token` do vendedor, que deve ser usado nas chamadas de API de criação de pagamento.
3.  **Credenciais:** Utilize as credenciais de teste (Test Access Token e Test Public Key) para evitar transações reais.

## 3. Fluxo de Pagamento com Split (API)

Ao criar um pagamento usando o **Checkout API**, o split é realizado através do parâmetro `application_fee`.

### Exemplo de Requisição (POST `/v1/payments`)

```json
{
    "description": "Pagamento de teste Marketplace",
    "transaction_amount": 100.00,
    "application_fee": 20.00,
    "payment_method_id": "master",
    "payer": {
        "email": "test_un@testuser.com"
    },
    "token": "CARD_TOKEN"
}
```

*   **Authorization Header:** `Bearer {Vendedor_Access_Token}` (Token obtido via OAuth).
*   **Split:** O Mercado Pago desconta primeiro sua própria taxa e depois distribui o valor:
    *   O Integrador recebe R$ 20,00 (especificado em `application_fee`).
    *   O Vendedor recebe o valor restante (R$ 80,00 - taxas do MP).

## 4. Fluxo de Pagamento com Split (Checkout Pro)

Para o **Checkout Pro**, utiliza-se o parâmetro `marketplace_fee` na criação da preferência.

### Exemplo de Requisição (POST `/checkout/preferences`)

```json
{
    "items": [
        {
            "title": "Produto Marketplace",
            "quantity": 1,
            "unit_price": 100.00
        }
    ],
    "marketplace_fee": 20.00
}
```

## 5. Simulação de Cenários com Cartões de Teste

Utilize os cartões de teste e os nomes de titulares específicos para simular diferentes status:

| Nome do Titular | Status Resultante |
| :--- | :--- |
| `APRO` | Aprovado |
| `FUND` | Recusado por saldo insuficiente |
| `CONT` | Pendente |
| `SECU` | Recusado por código de segurança |

## 6. Verificação de Reembolsos (Refunds)

No modelo de split:
- O reembolso é **proporcional** entre o vendedor e o marketplace.
- O marketplace não pode realizar o reembolso total se o vendedor não tiver saldo suficiente em conta (em modelos 1:1).

---
*Referência: [Documentação Marketplace Mercado Pago](https://www.mercadopago.com.br/developers/pt/docs/split-payments/landing)*
