# Integração Checkout Pro API - Erro de processamento genérico no Sandbox

Olá equipe de suporte do Mercado Pago.
Estamos integrando o Checkout Pro em nossa aplicação React Native (Expo) com backend Node/Python e fluxo de pagamento no modelo **Marketplace (com split e cobrança de taxa de comissão)**.
Seguimos toda a documentação oficial para criação de usuários de teste e preenchimento de dados de simulação (como `APRO`), mas encontramos um comportamento de transação recusada de forma genérica na finalização da compra no ambiente Sandbox, sem que o backend sequer seja notificado via Webhook desse pagamento específico.

## 1. Arquitetura da Integração
- **Tipo de Checkout:** Checkout Pro (preferência gerada via API `POST /checkout/preferences` usando OAuth).
- **Modelo de Integração:** Marketplace Split Payment. O backend usa as credenciais de Produção do **Vendedor** (obtidas via fluxo OAuth `authorization_code`) para criar a preferência de checkout com `marketplace_fee` destinado ao **Integrador**.
- **Front-end:** React Native (Expo Go) usando a biblioteca `expo-web-browser` para abrir a URL `init_point` gerada pelo Mercado Pago e voltar ao app via Deep Links configurados em `back_urls`.

## 2. Passo a Passo do Erro

1. O backend recebe do aplicativo a ordem de criar o checkout com determinados itens.
2. O backend envia uma requisição `POST /checkout/preferences` autenticando com o `access_token` do Vendedor de teste (recuperado do nosso banco após a vinculação OAuth).
3. A preferência é criada com **sucesso**. Nós recebemos o `id` da preferência e o `init_point`.
4. O app React Native aciona `WebBrowser.openAuthSessionAsync` com o `init_point`. A tela do Mercado Pago abre corretamente no dispositivo.
5. Selecionamos "Pagar como Convidado" ou "Nova Conta".
6. Inserimos o e-mail de um Usuário de Teste ativo do tipo **Comprador** (`buyer`), configurado para o mesmo `site_id` (MLB).
7. Preenchemos os dados de cartão Mastercard de teste (`5031 4332 1540 6351`), Venc. `11/30`, CVV `123`.
8. Preenchemos o Nome do Titular *estritamente* como **APRO** (para forçar aprovação conforme [documentação](https://www.mercadopago.com.br/developers/pt/docs/checkout-api-payments/additional-content/your-integrations/test/cards)), e informamos um CPF brasileiro válido (simulado).
9. Ao clicar em **Pagar**, a tela do Mercado Pago processa por alguns segundos e, em seguida, redireciona o usuário para um endereço de erro:

   `https://www.mercadopago.com.br/checkout/v1/payment/redirect/{UUID}/congrats/recover/error/?preference-id={PREFERENCE_ID}&router-request-id={ROUTER_ID}`

   A mensagem exibida em tela é: **"Ocorreu um erro, Não foi possível processar seu pagamento"**.
10. Nenhum webhook novo de tipo `payment` chega ao nosso backend informando o ID dessa tentativa falha. O webhook está operante pois webhooks de `merchant_order` e webhooks simulados via painel chegam com HTTP 200 normal.

## 3. Informações da Integração (Evidências)

- **País:** Brasil (MLB)
- **ID do Aplicativo (Client ID do Integrador):** [6512191298559402]
- **Preference ID (exemplo de falha recente):** `3207386125-d8ebdb07-0375-4cc2-ab14-caecf77ee2c6`
- **Link de redirecionamento que gerou o erro:** `https://www.mercadopago.com.br/checkout/v1/payment/redirect/745bcb22-6a14-4d87-8647-f08ed6933252/congrats/recover/error/?preference-id=3207386125-d8ebdb07-0375-4cc2-ab14-caecf77ee2c6&router-request-id=a3f8fed2-649e-4579-a28e-f5a6dad79291&p=f4771916f50f4ecb303d7c8b0093e937`
- **ID da conta Vendedor (Seller de Teste):** TESTUSER7767014334974603516
- **E-mail do Comprador (Buyer de Teste usado):** TESTUSER8917601619045298291

### Payload de Criação da Preferência enviado pelo Backend
Abaixo, a cópia do JSON enviado ao `POST /checkout/preferences` (as chaves foram simplificadas para facilitar a leitura), autenticado no Bearer Token gerado via OAuth pelo Seller:

```json
{
  "items": [
    {
      "id": "AULA-123",
      "title": "Aula de Direção - GoDrive",
      "description": "Aula de direção",
      "category_id": "services",
      "quantity": 1,
      "unit_price": 100.0,
      "currency_id": "BRL"
    }
  ],
  "marketplace_fee": 15.0,
  "back_urls": {
    "success": "godrive://payment/success",
    "pending": "godrive://payment/pending",
    "failure": "godrive://payment/error"
  },
  "auto_return": "all",
  "binary_mode": true,
  "payer": {
    "email": "[EMAIL_DO_COMPRADOR_DE_TESTE]"
  },
  "statement_descriptor": "GODRIVE AULA",
  "external_reference": "[UUID_DO_GRUPO_DA_COMPRA]"
}
```

## 4. O que já verificamos

1. Ambas as contas (Seller e Buyer de teste) estão sob o **mesmo país (MLB)** e foram geradas no painel da **nossa aplicação principal** (Painel de Integrações > Contas de Teste).
2. O `access_token` usado na rota `/checkout/preferences` não é o do Integrador, mas o `access_token` do **Vendedor de teste** retornado após ele executar o login OAuth no nosso app.
3. Testamos abrindo o `init_point` do checkout em abas anônimas para evitar sobreposição de cache/sessão.
4. O `card_holder` do cartão foi preenchido exata e unicamente como **APRO**.

Poderiam verificar pelos IDs da transação (`preference-id=3207386125-d8ebdb07-0375-4cc2-ab14-caecf77ee2c6` | `router-request-id=a3f8fed2-649e-4579-a28e-f5a6dad79291`) por que as simulações validas do Checkout Pro estão sendo recursivamente barradas sem notificar a API? Há alguma restrição que ignoramos com relação ao `marketplace_fee` ou à validação de `payer.email` vs e-mail logado? Agradecemos a assistência.
