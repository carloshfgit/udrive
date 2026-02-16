# Estudo de Migração: Stripe para Mercado Pago (GoDrive)

Este documento detalha a análise técnica e o modelo de integração para a migração do processamento de pagamentos do Stripe para o **Mercado Pago**, utilizando a tecnologia de **Checkout Pro**.

## 1. Checkout Pro: Modelo de Integração

O Checkout Pro é a solução de redirecionamento do Mercado Pago. Ao contrário do Bricks (onde o formulário fica no seu site), o Checkout Pro direciona o usuário para uma página segura do Mercado Pago, onde ele pode escolher meios de pagamento salvos em sua conta ou pagar com Pix, Boleto e Cartão como convidado.

### Vantagens do Checkout Pro:
1.  **Segurança:** Toda a conformidade PCI DSS é tratada pelo Mercado Pago.
2.  **Conversão:** Permite que usuários paguem rapidamente usando saldo da conta MP ou cartões já salvos.
3.  **Facilidade:** Menos código no frontend; o Mercado Pago cuida da UI de pagamento e seleção de parcelas.
4.  **Omnichannel:** Funciona bem em web, mobile web e via SDKs mobile.

### Fluxo de Implementação

#### Passo 1: Criar uma Preferência (Backend)
O servidor do GoDrive faz uma requisição para criar uma "Preferência de Pagamento".

```json
// POST https://api.mercadopago.com/checkout/preferences
// Header: Authorization: Bearer {SELLER_ACCESS_TOKEN}
{
  "items": [
    {
      "id": "AULA-123",
      "title": "Aula de Direção - 1h",
      "quantity": 1,
      "currency_id": "BRL",
      "unit_price": 100.00
    }
  ],
  "marketplace_fee": 20.00, // Taxa do GoDrive (Comissão + Taxas)
  "back_urls": {
    "success": "https://godrive.com/payment/success",
    "failure": "https://godrive.com/payment/failure",
    "pending": "https://godrive.com/payment/pending"
  },
  "auto_return": "approved"
}
```

#### Passo 2: Redirecionar o Usuário (Frontend)
O backend retorna um `init_point`. O frontend redireciona o usuário ou abre o checkout em um modal/overlay.

```javascript
// Usando o SDK v2
const mp = new MercadoPago('YOUR_PUBLIC_KEY');
mp.checkout({
  preference: {
    id: 'ID_DA_PREFERENCIA_GERADA'
  },
  autoOpen: true, // Abre o checkout automaticamente
});
```

---

## 2. Mercado Pago Marketplace vs. Stripe Connect

O GoDrive opera como um **Marketplace**. Para realizar o split de pagamento com Checkout Pro:

| Conceito Stripe | Equivalente Mercado Pago | Observação |
| :--- | :--- | :--- |
| **Connected Account** | **Vendedor Autorizado (OAuth)** | O instrutor autoriza o GoDrive. Usamos o `access_token` dele nas chamadas de API. |
| **Application Fee** | **marketplace_fee** | Definido no objeto da preferência. O valor vai direto para a conta do GoDrive. |
| **Direct Charge** | **Checkout Pro com Token do Vendedor** | A transação acontece na conta do vendedor, descontando a taxa do Marketplace. |

---

## 3. Gestão de Custódia e Split (Marketplace)

No Checkout Pro, a divisão do dinheiro acontece no momento da aprovação do pagamento.

### Fluxo de Split no GoDrive:
1.  **OAuth:** O instrutor vincula sua conta Mercado Pago ao GoDrive.
2.  **Criação da Preferência:** No backend, ao criar a preferência, o GoDrive usa o `access_token` do instrutor e define o `marketplace_fee`.
3.  **Recebimento:** 
    *   O Mercado Pago desconta a taxa de processamento deles (ex: 4,98%).
    *   O Mercado Pago desconta a `marketplace_fee` (taxa do GoDrive) e transfere para a conta da plataforma.
    *   O restante fica na conta do instrutor.

> [!TIP]
> **Modo Binário:** Para evitar pagamentos que fiquem "pendentes" por muito tempo (como boletos que o usuário esquece), podemos ativar o `binary_mode: true` na preferência, aceitando ou recusando o pagamento na hora.

---

## 4. Tabela de Taxas (Brasil)

Taxas vigentes para recebimento no momento (Checkout Pro):

| Meio de Pagamento | Taxa (%) / Valor | Dinheiro Disponível |
| :--- | :--- | :--- |
| **Cartão de Crédito** | 4,98% | Na hora* |
| | 4,49% | 14 dias |
| | 3,98% | 30 dias |
| **Pix** | 0,99% | Na hora |
| **Saldo Mercado Pago** | 4,99% | Na hora |
| **Boleto** | R$ 3,49 | 1 a 2 dias úteis |

---

## 5. Próximos Passos para Integração

1.  **Vincular Aplicação:** Utilizar as credenciais da aplicação `TestApp-121d22b9` para testes iniciais.
2.  **Implementar Fluxo OAuth:** Criar a rota no backend para receber o código do instrutor e trocar pelo `access_token`.
3.  **Configurar Webhooks:** Escutar eventos de `payment` para atualizar o status das aulas no banco de dados do GoDrive.
4.  **Sandbox:** Realizar ciclos de testes completos usando usuários de teste (Buyer e Seller).

---
*Documento atualizado para priorizar o Checkout Pro como modelo de integração inicial.*
