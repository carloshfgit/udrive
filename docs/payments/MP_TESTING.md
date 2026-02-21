# Fluxo de Testagem Mercado Pago: Marketplace e Split de Pagamentos em React Native (Expo Go)

Este guia detalha o processo completo para testar a integração do **Checkout Pro** no GoDrive (modelo Marketplace) usando **React Native (Expo Go)**, de acordo com a documentação oficial do Mercado Pago.

---

## 1. Contas de Teste Necessárias

Para testar o fluxo de ponta a ponta (E2E) em um ambiente de Marketplace (com split de pagamentos), você deve criar suas contas no **Painel de Integrações do Mercado Pago**. É mandatório o uso de usuários de teste, pois transações com usuários reais não funcionam com credenciais de teste, e credenciais de produção exigem pagamentos reais.

O ecossistema exige **3 contas de teste** distintas:

1.  **Integrador (Marketplace / GoDrive):** É a sua conta principal onde a Aplicação (App ID) está criada. Essa aplicação define as credenciais base e recebe o `marketplace_fee` (taxa de comissão).
2.  **Vendedor (Seller / Instrutor):** Conta que representa o instrutor. 
    - Deve autorizar a conta do Integrador através do fluxo OAuth.
    - É o recebedor do valor principal.
3.  **Comprador (Buyer / Aluno):** Conta utilizada para entrar no Checkout Pro e efetuar a compra com cartões de teste ou saldo fictício.

> [!IMPORTANT]
> - O **Comprador** e o **Vendedor** precisam obrigatoriamente ser criados com o **mesmo país de operação** (ex: Brasil - MLB).
> - Ao criar a conta do Comprador, adicione **dinheiro fictício** se quiser testar pagamentos via Saldo Mercado Pago.

**Como criar as contas:**
1. Navegue até o [Painel do Desenvolvedor (Suas Integrações)](https://www.mercadopago.com.br/developers/panel/app).
2. Vá na seção **Contas de teste** da sua aplicação.
3. Clique em **+ Criar conta de teste**, escolha o País, forneça uma descrição e selecione o tipo (Vendedor ou Comprador).
4. Guarde o Username e a Senha gerados automaticamente para fazer os logins.

---

## 2. Testando no App Expo Go (Mobile)

Em aplicativos móveis, a recomendação oficial do Mercado Pago não é mais usar `WebViews` internas para exibir o Checkout, pois isso frequentemente esbarra em bloqueios de segurança do MP (autenticações, biometria, login).

A forma correta no ecossistema do Expo é usando o **Navegador Nativo Seguro (Custom Tabs no Android / Safari View Controller no iOS)**. No GoDrive, isso é feito com a biblioteca `expo-web-browser`.

### 2.1. Fluxo de Execução no App

1. O backend do GoDrive processa o carrinho, cria a preferência via API (usando o `access_token` do Instrutor/Seller e definindo o `marketplace_fee`), e devolve a URL (`init_point`).
2. O aplicativo mobile chama `WebBrowser.openAuthSessionAsync(init_point, ...)` ou `WebBrowser.openBrowserAsync()`.
3. O aluno (usando a conta de Comprador) faz login na interface web do MP que foi aberta ou entra como Convidado.
4. O aluno preenche os dados do cartão de teste (veja a seção de Cartões abaixo) e realiza o pagamento.
5. O redirecionamento de volta ao app ocorre via **Deep Links**.

### 2.2. Configuração de Deep Links (`back_urls`)

Para voltar ao aplicativo React Native Expo Go de forma fluida após o teste:

- No backend, ao criar a preferência, as `back_urls` devem apontar para o `scheme` configurado no `app.json` do Expo (ex: `godrive://`).
```json
{
  "back_urls": {
    "success": "godrive://payment/success",
    "pending": "godrive://payment/pending",
    "failure": "godrive://payment/error"
  },
  "auto_return": "approved"
}
```
- No frontend (App.tsx), o `Linking.addEventListener` captura o link `godrive://...`, permite fechar o navegador webview (usando `WebBrowser.dismissBrowser()`) e redireciona a interface para a tela de `PaymentResultScreen`.

---

## 3. Cartões de Teste e Cenários de Validação

O Mercado Pago disponibiliza cartões de crédito e débito cujos números passam na validação do formulário, mas não geram cobranças reais em um ambiente de Sandbox.

### Números de Cartões (Exemplo Brasil - MLB)

| Bandeira         | Tipo    | Número do Cartão      | CVV  | Venc. |
| :--------------- | :------ | :-------------------- | :--- | :---- |
| Mastercard       | Crédito | 5031 4332 1540 6351   | 123  | 11/30 |
| Visa             | Crédito | 4235 6477 2802 5682   | 123  | 11/30 |
| American Express | Crédito | 3753 651535 56885     | 1234 | 11/30 |
| Elo              | Débito  | 5067 7667 8388 8311   | 123  | 11/30 |

### Simulando Diferentes Status de Pagamento

O "segredo" para induzir resultados diferentes (sucesso, recusado, pendente) na versão de testes é preencher o campo **Nome do titular (Cardholder Name)** de forma específica e fornecer um CPF de teste qualquer (e.g., `12345678909`).

| Nome do Titular a preencher | Resultado Simulado pela API Mercado Pago        | Comportamento esperado no App GoDrive |
| :-------------------------- | :---------------------------------------------- | :------------------------------------ |
| `APRO`                      | **Aprovado** (`status: approved`)               | Redireciona via App Deep Link para *Success*. Webhook atualiza no backend e a aula é confirmada. |
| `CONT`                      | **Pendente** (`status: pending` / `in_process`)| Redireciona para tela de acompanhamento/pendente. |
| `OTHE`                      | **Recusado** (Erro geral)                       | Redireciona para *Error*. Aluno pode tentar novamente. |
| `FUND`                      | **Recusado** (Saldo insuficiente)               | Erro de pagamento negado. |
| `SECU`                      | **Recusado** (CVV Inválido)                   | Erro de pagamento negado. |
| `EXPI`                      | **Recusado** (Cartão expirado)                 | Erro de pagamento negado. |

## 4. Testando a Vinculação de Conta (OAuth) no App Instrutor

Para testar o fluxo onde o Instrutor vincula sua conta do Mercado Pago usando o Expo Go no dispositivo físico, é necessário configurar o seu ambiente local para receber o *callback* de autorização.

### 4.1. Expondo o Backend Local
O celular (via `expo-web-browser`) e os servidores do Mercado Pago precisam de uma URL publicamente acessível que aponte para o seu backend rodando localmente na porta 8000. Utilizaremos o **ngrok** para isso:

Execute o comando no seu terminal:
```bash
ngrok http 8000 --url kinetic-unhazily-masako.ngrok-free.dev
```
*(Nota: este é o seu domínio estático configurado)*

### 4.2. Configurando as Variáveis de Ambiente
Atualize a variável `MP_REDIRECT_URI` no arquivo `backend/.env` do seu projeto com o caminho correto da rota de instrutor:

```env
MP_REDIRECT_URI=https://kinetic-unhazily-masako.ngrok-free.dev/api/v1/instructor/oauth/mercadopago/callback
```

### 4.3. Configurando a Aplicação no Mercado Pago
1. Acesse o [Painel de Integrações do Mercado Pago](https://www.mercadopago.com.br/developers/panel/app).
2. Selecione sua Aplicação (GoDrive).
3. No menu lateral, clique no ícone de lápis em seguida salve a URL em **URLs de Redirecionamento**.
4. Adicione **exatamente a mesma URL** que você configurou no seu `.env` e salve:
   `https://kinetic-unhazily-masako.ngrok-free.dev/api/v1/instructor/oauth/mercadopago/callback`

### 4.4. Executando o Teste no Celular
1. Abra o app do Instrutor no Expo Go.
2. Na tela de perfil, clique em **Vincular conta Mercado Pago**.
3. O app abrirá um navegador interno (in-app browser).
4. Faça o login utilizando uma conta de teste do tipo **Vendedor (Seller)**.
5. Após você autorizar, o Mercado Pago redirecionará para a sua URL do ngrok. O backend processará a vinculação e retornará um JSON confirmando o sucesso.
6. Feche o navegador interno manualmente (botão "X" ou "Concluído"). A tela do aplicativo se atualizará, mostrando que a conta foi vinculada ("Sua conta já está vinculada ✅").

### 4.5. Solução de Problemas no OAuth (Troubleshooting)

**Erro comum**: Ao abrir o link de autorização, o Mercado Pago exibe a mensagem *"O aplicativo não está pronto para se conectar ao Mercado Pago"*, a tela fica parada e o backend não recebe nenhum *callback*.

**Possíveis causas e soluções:**

1. **Divergência na URL de Redirecionamento (Redirect URI)**
   - **Causa**: O parâmetro `redirect_uri` enviado na URL do OAuth pela sua aplicação não é **exatamente igual** à "URL de Redirecionamento" salva no Painel do Desenvolvedor do Mercado Pago.
   - **Solução**: Verifique se a URL da variável `MP_REDIRECT_URI` no seu `.env` confere letra por letra com o configurado em **Autenticação e Segurança > URLs de Redirecionamento** na sua Aplicação no Mercado Pago (incluindo `https://`, ausência de barra `/` no final, domínio exato do ngrok, etc).

2. **Divergência de País (Site ID) do Usuário de Teste**
   - **Causa**: O usuário de teste do tipo "Vendedor" (Seller) utilizado no login possui um país diferente (ex: MLM - México) do país da sua Aplicação / Integrador (ex: MLB - Brasil).
   - **Solução**: Certifique-se de criar e fazer login no fluxo OAuth utilizando uma **conta de teste Vendedor** do **mesmo país** da conta principal (Integrador).

3. **Tentativa de Autenticação Incorreta**
   - **Causa**: Tentar realizar a autorização usando a própria conta desenvolvedora (dona da Aplicação) ao invés de uma conta de teste, ou usar uma conta de teste que não foi criada pela sua conta desenvolvedora.
   - **Solução**: A vinculação em ambiente de testes deve ser estritamente feita com uma **conta de teste (perfil Vendedor)** gerada dentro da guia "Contas de teste" da sua própria aplicação no Mercado Pago.

4. **Credenciais Incorretas (Client ID)**
   - **Causa**: O `client_id` (App ID) passado na URL de autorização está incorreto, ausente, revogado ou com permissões mal configuradas.
   - **Solução**: Cheque se o `MP_CLIENT_ID` no backend corresponde ao "ID do aplicativo" ativo. Verifique também no painel se as permissões necessárias para o OAuth estão ativas.

> [!TIP]
> Para evitar conflitos de sessão ou cache persistente, sempre copie a URL gerada para OAuth e abra-a em uma **janela anônima** do navegador do computador na hora de testar a vinculação com as senhas dos usuários de teste.

---

## 5. Testando Webhooks Localmente

Como o backend está executando no Docker para testes locais, o Mercado Pago na nuvem não consegue chegar a `localhost`. Para que as notificações funcionem nos seus testes locais, o Mercado Pago precisa de uma URL pública na internet que direcione para o seu ambiente de desenvolvimento.

Para isso, siga os passos abaixo:

### 5.1. Expondo o Ambiente Local com Ngrok
Mantenha o ngrok rodando no seu terminal. Ele criará um túnel reverso apontando para a porta 8000 do seu backend:
```bash
ngrok http 8000 --url kinetic-unhazily-masako.ngrok-free.dev
```
*Isso usará a URL `https://kinetic-unhazily-masako.ngrok-free.dev`.*

### 5.2. Configurando o Webhook no Painel do Mercado Pago
1. Acesse o [Painel do Desenvolvedor (Suas Integrações)](https://www.mercadopago.com.br/developers/panel/app).
2. Selecione a sua aplicação (GoDrive).
3. No menu lateral, expanda a seção **Notificações** e clique em **Webhooks**.
4. No campo **URL de Produção** e **URL de Teste**, insira a URL completa apontando para a rota específica do seu backend:
   ```text
   https://kinetic-unhazily-masako.ngrok-free.dev/api/v1/shared/webhooks/mercadopago
   ```
   *(Exemplo: `https://kinetic-unhazily-masako.ngrok-free.dev/api/v1/shared/webhooks/mercadopago`)*
5. Na seção **Eventos**, selecione os tópicos que deseja receber. Para o fluxo de pagamentos, selecione pelo menos **Payments** (`payment`).
6. Salve as configurações.

### 5.3. Usando a Ferramenta de Simulação do Mercado Pago
O painel do Mercado Pago oferece uma ferramenta para enviar eventos simulados, ideal para verificar se o seu backend está recebendo e processando (validando a assinatura HMAC `x-signature`) corretamente sem precisar criar compras reais de teste.

1. Na mesma tela de configuração de **Webhooks**, após salvar a URL, procure pela seção **Simular evento** (ou botão similar).
2. Selecione o evento (`payment`).
3. Clique em **Enviar teste**.
4. Observe os logs do seu backend no Docker (`docker compose logs -f backend`). Você deverá ver uma mensagem indicando o recebimento do webhook (ex: `Webhook MP recebido: type=payment...`) e o retorno HTTP `200 OK`.

### 5.4. Validando o Fluxo Completo E2E
Ao realizar uma compra pelo aplicativo mobile (usando o cartão de teste aprovado e a conta de comprador), o próprio Mercado Pago enviará a notificação real (em modo Live/Test) para a URL configurada. Verifique se o backend processa a notificação e atualiza o status do `Payment` no banco de dados para `COMPLETED`.

## 6. Solução de Problemas Comuns (Troubleshooting)

### Erro Genérico no Checkout Pro: "Ops, ocorreu um erro" ao finalizar compra como convidado no Sandbox
Se durante uma compra de teste o aluno entrar como **convidado** no Checkout Pro, preencher os dados do cartão de teste e ao clicar em pagar receber a mensagem genérica **"Ops, ocorreu um erro"** na plataforma do Mercado Pago (sem que a requisição chegue ao backend), as causas mais comuns são:

1. **Sessão Conflitante no Navegador (Muito Comum):**
   - **Causa:** O navegador (ou Custom Tab/WebView no mobile) possui cookies armazenados e já está logado em uma conta real do Mercado Pago/Mercado Livre, ou logado na conta do próprio Vendedor. O Mercado Pago bloqueia a transação de teste ao detectar o conflito.
   - **Solução:** Se estiver testando no Expo, limpe os dados do navegador padrão do aparelho. Se estiver na Web, use sempre uma **janela anônima** para abrir o link do Checkout.

2. **Tentativa de "Pagar a si mesmo":**
   - **Causa:** O Checkout não permite que o e-mail do comprador seja igual ao e-mail da conta recebedora (Instrutor) ou da conta principal (Integrador), mesmo na opção "Convidado".
   - **Solução:** Na hora de preencher os dados de convidado no Checkout, utilize estritamente o e-mail de um **Usuário de Teste do tipo Comprador** (ex: `test_user_XXXX@testuser.com`), gerado no painel do Mercado Pago.

3. **Nome do Titular do Cartão Incorreto para o Sandbox:**
   - **Causa:** Em ambiente de testes, o Mercado Pago exige que o **Nome do Titular** seja preenchido com comandos de simulação específicos. Preencher um nome aleatório/real fará com que o cartão de teste seja rejeitado pelas validações bancárias simuladas, resultando em erro genérico.
   - **Solução:** Preencha o nome do titular com o prefixo exato exigido para o cenário de teste (ex: coloque `APRO` no nome do titular se quiser aprovar o pagamento, ou `OTHE` para simular recusa).

4. **Inconsistência de Credenciais em Marketplace (Split):**
   - **Causa:** A preferência de pagamento foi gerada com o `access_token` de uma conta de Produção, mas o cartão usado é de Teste. Em Marketplaces, outro erro comum é gerar a _preference_ com o `access_token` do integrador em vez do `access_token` do vendedor (Instrutor) obtido via OAuth.
   - **Solução:** Certifique-se de que está usando credentials de Teste do Vendedor correto (Seller) obtidas na autorização OAuth no momento de gerar a chamada `/checkout/preferences`.

5. **Falha de Validação Silenciosa no País:**
   - **Causa:** Os cartões fictícios (ex: baseados no Brasil - MLB) são incompatíveis caso a conta de teste do Vendedor tenha sido registrada para outro país (ex: MLM - México). Isso retorna erro na finalização.
   - **Solução:** Confirme no painel que o Integrador, a Conta Teste Vendedor e a Conta Teste Comprador estão todas sob o mesmo _Site ID_ (MLB).

---
*Referência do material pesquisado:*
* [Contas de teste - Mercado Pago Docs](https://www.mercadopago.com.br/developers/pt/docs/checkout-api-payments/additional-content/your-integrations/test/accounts)
* [Cartões de teste - Mercado Pago Docs](https://www.mercadopago.com.br/developers/pt/docs/checkout-api-payments/additional-content/your-integrations/test/cards)
* [Checkout Pro em React Native (Integração Expo)](https://www.mercadopago.com.br/developers/pt/docs/checkout-pro/mobile-integration/react-native-expo-go)
