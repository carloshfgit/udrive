Problema: 
- Aluno abre o checkout como convidado, preenche os dados do cartão de teste, aluno tenta finalizar a compra ja na pagina do mercado pago e a mesma retorna um erro genérico. "Ops, ocorreu um erro." Backend não retorna nenhum log relacionado ao erro. (Esse problema aparece apenas com instrutores que criei e fiz o fluxo oAuth manualmente via app, Roberta Silva e Alfredo Lopes).
- ATUALIZAÇÃO: ao usar o "Novo Intrutor" (novo_instrutor@example.com) criado e autenticado via script, o erro genérico desapareceu. No entanto uma nova tela de erro apareceu: Ocorreu um erro...  Não foi possível processar seu pagamento. E agora logs aparecem no backend:
LOGS:
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
