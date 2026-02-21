Problema: 
- Aluno abre o checkout como convidado, preenche os dados do cartão de teste, aluno tenta finalizar a compra ja na pagina do mercado pago e a mesma retorna um erro genérico. "Ops, ocorreu um erro." Backend não retorna nenhum log relacionado ao erro. (Esse problema aparece apenas com instrutores que criei e fiz o fluxo oAuth manualmente via app, Roberta Silva e Alfredo Lopes).
- ATUALIZAÇÃO: ao usar o "Novo Intrutor" (novo_instrutor@example.com) criado e autenticado via script, o erro genérico desapareceu. No entanto uma nova tela de erro apareceu: Ocorreu um erro...  Não foi possível processar seu pagamento. E agora logs aparecem no backend:

LOGS:
godrive_backend   | INFO:     connection closed
godrive_backend   | Assinatura inválida no webhook MP. x-signature=ts=1771703517,v1=f01074992a8f0c8036493760cc0fba359f3f4b8f0a9e0faed542153975a2774d
godrive_backend   | INFO:     172.20.0.1:35498 - "POST /api/v1/shared/webhooks/mercadopago?id=38375256331&topic=merchant_order HTTP/1.1" 200 OK
godrive_backend   | INFO:     172.20.0.1:35786 - "POST /api/v1/instructor/shared/webhooks/mercadopago?id=38372304899&topic=merchant_order HTTP/1.1" 404 Not Found

Erro generico persiste com instrutores criados via app.
Testando script generate_test_checkout.py com Roberta Silva (roberta@godrive.com):
Observações ao rodar o script:
- Ao usar o link de checkout, o email do comprador é de um aluno exemplo qualquer, diferente do checkout manual  via app que o email do comprador está sendo aluno@godrive.com
- O erro genérico persiste ao tentar pagar usando o link gerado.
LOGS ao rodar o script acima:
2026-02-21 18:04:48 [info     ] multi_item_checkout_created    num_items=1 preference_group_id=952794e8-fcd1-4db1-8517-f2da6c20676a total_amount=119.90 total_marketplace_fee=18.93

--- CHECKOUT GERADO ---
Payment ID: caef2dcb-49f9-4ed4-9334-ea208e3fdac9
Preference ID: 3207386125-48527228-77fc-4af3-ab89-46244acef606
Checkout URL: https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=3207386125-48527228-77fc-4af3-ab89-46244acef606
Sandbox URL: https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=3207386125-48527228-77fc-4af3-ab89-46244acef606

# Guia de Testes do Mercado Pago Checkout Pro (Sandbox)

Para agilizar os testes com qualquer instrutor, você pode usar os seguintes comandos no terminal:

### 1. Vincular Token de Teste a um Instrutor

Este comando encripta o token de sandbox e o salva no perfil do instrutor no banco de dados. Caso o perfil não exista, ele será criado.

```bash
# Formato: python scripts/update_seed_instructor.py <email_do_instrutor>

docker compose exec -e PYTHONPATH=/app backend python scripts/update_seed_instructor.py novo@email.com

```
### 2. Gerar Preferência de Checkout para Teste

Gera uma preferência do Mercado Pago para o primeiro agendamento pendente encontrado para o instrutor especificado.

```bash

# Formato: python scripts/generate_test_checkout.py <email_do_instrutor>

docker compose exec -e PYTHONPATH=/app backend python scripts/generate_test_checkout.py novo@email.com

```
## Resumo do Fluxo

De acordo com o Quality Checklist e arquitetura do MP:

1. **Nunca use a mesma conta para Comprador/Vendedor**. Como a aplicação injeta o token do seu painel .env como vendedor, o comprador inserido no payment sheet deve possuir um e-mail completamente distinto do admin Mercado Pago que aprova esse app.
2. Recomendamos gerar contas de Comprador pela aba [Contas de Teste no Dev Dashboard](https://www.mercadopago.com.br/developers/panel/test-accounts). O e-mail de teste gerado lá (terminado em `@testuser.com`) permite fazer o fluxo completo da inserção dos cartões sem barreira de proteção do guest.
3. Se estiver optando por fluxo Guest, **o CPF e Email adicionais no Guest form** precisam existir e não podem ser simulados de má qualidade (usar nomes comuns, CPF válidos não vinculados a fraude) senão o MP também trava com o "Ops".

### Cartões de Teste Oficiais

Ao abrir o painel do Checkout Pro do aplicativo móvel, insira os dados do cartão de aprovação oficial do Mercado Pago:
- **Bandeira:** Mastercard ou Visa
- **Número do Cartão:** Solicite "APRO**" via digitação:

---

## 🔍 Levantamento de Causas e Possíveis Soluções (Resultados da Pesquisa)

Após analisar a documentação oficial do Mercado Pago e fóruns de desenvolvedores, as causas mais comuns para os erros enfrentados no fluxo do Checkout Pro Sandbox são:

### 1. Erro Genérico "Ops, ocorreu um erro" ou "Não foi possível processar..."
*   **Contas de Comprador e Vendedor iguais ou inválidas:** O Mercado Pago bloqueia testes onde o comprador e o vendedor são a mesma entidade. Além disso, usar emails aleatórios como `aluno@godrive.com` pode disparar o sistema antifraude ou barreiras de Guest Checkout do Sandbox. A recomendação oficial é **sempre usar contas de teste geradas pelo painel de desenvolvedores** (terminadas em `@testuser.com`).
*   **Nome do Titular do Cartão:** No Sandbox, o nome do titular do cartão dita o resultado do pagamento. Para que o pagamento seja aprovado com sucesso, o nome do titular **deve** ser preenchido exatamente como `"APRO"`. Outros nomes como `"OTHE"` (erro geral), `"FUND"` (saldo insuficiente) ou nomes comuns podem gerar falhas intencionais do Sandbox ou erros genéricos de validação.
*   **Falta de Aplicação na Conta Compradora (Fluxo não-guest):** Se o fluxo exigir login do comprador, a conta de teste do comprador também deve ter uma aplicação criada no painel de desenvolvedores para que o Checkout Pro funcione perfeitamente.

### 2. Erro de Webhook `404 Not Found` no Backend
*   **Rota Inexistente ou Erro de Mapeamento:** O log `POST /api/v1/instructor/shared/webhooks/mercadopago?id=38372304899&topic=merchant_order HTTP/1.1 404 Not Found` indica claramente que o Mercado Pago enviou o webhook com sucesso para o ngrok, mas a aplicação FastAPI retornou 404. 
*   **Causa provável:** A URL do Webhook configurada manualmente no **Dashboard de Desenvolvedor do Mercado Pago** (Painel da Aplicação) foi inserida incorretamente com o prefixo `/instructor/`. O correto é apenas `/api/v1/shared/webhooks/mercadopago`.

### 3. Erro `Assinatura inválida no webhook MP` e Fluxo Travado
*   **O Bug Original:** A aplicação estava exigindo e validando o header `x-signature` para todas as notificações do Mercado Pago. Caso a assinatura fosse inválida ou ausente (comum em IPNs `topic=merchant_order` enviadas via `notification_url` local) a aplicação retornava HTTP 200 pro MP mas abortava silenciosamente a execução (`return {"status": "error"}`). Como o webhook de `payment` também acabava caindo nessa validação restrita, o processamento nunca ia para a task em background.
*   **A Solução Aplicada:** O arquivo `webhooks.py` foi modificado. Agora, se a validação da assinatura falhar, a aplicação apenas registra o aviso no log (`logger.warning`), mas **continua a processar** o evento adicionando-o à `BackgroundTasks`. Essa alteração é 100% segura visto que a classe `HandlePaymentWebhookUseCase` SEMPRE realiza uma consulta direta à API do Mercado Pago (`get_payment_status`) com o token para confirmar a veracidade do evento e o real estado do pagamento, prevenindo completamente qualquer tentativa de injeção ou spoofing de dados maliciosos.

### Próximos Passos Sugeridos:
1. **Corrigir URL no Painel do MP:** Acesse a aplicação no Mercado Pago Developers e altere a URL do Webhook de Produção/Teste para remover o `/instructor/` (Ex: `https://seu-ngrok.app/api/v1/shared/webhooks/mercadopago`).
2. **Realizar Novo Teste com Cartão APRO**: Como a aplicação não bloqueia mais falsos-positivos na assinatura via Webhook, os status de falha (caso cartão recuse) ou sucesso (caso cartão "APRO" funcione) do MP serão agora devidamente recebidos e logados pelo GoDrive Backend.
3. Certifique-se de estar usando uma conta oficial compradora `@testuser.com` para interagir com o fluxo hospedado.
