# Análise de Impacto: Precificação Variável para Instrutores

Esta documentação detalha a análise arquitetural, de frontend e de integrações (especialmente Mercado Pago) referente à nova feature de precificação dinâmica, em que os instrutores podem definir preços distintos baseados na **Categoria da CNH (A/B)** e se o veículo utilizado será **do Instrutor ou do Aluno**.

---

## 1. Frontend do Aluno (Reserva, Carrinho e Checkout)

### 1.1. Fluxo de Seleção e Validação
A jornada do aluno ganhará uma etapa a mais de configuração da aula **antes** ou **durante** a escolha de horário:
- **Seleção Dinâmica:** Quando o aluno visualiza o perfil do instrutor, o frontend deve verificar quais dos 4 preços (`price_cat_a_instructor_vehicle`, `price_cat_a_student_vehicle`, `price_cat_b_instructor_vehicle`, `price_cat_b_student_vehicle`) estão preenchidos (`!== null`).
- **Desabilitação de Opções:** Se um instrutor não aceita veículo do aluno para a Categoria A (ex: valor nulo), a UI deve bloquear essa combinação.
- **Transparência de Preço:** O preço final calculado (aplicando o *markup* da plataforma sobre o preço base) deve ser reativo às seleções do usuário na tela, recalculando instantaneamente.

### 1.2. Atualização dos Requests
- O DTO do carrinho e do checkout (ex: `CreateCheckoutDTO`) deverá enviar os novos metadados: `lesson_category` (A/B/AB) e `vehicle_ownership` (Instructor/Student) atrelados a cada `scheduling_id`. Em alternativa, esses metadados devem ser definidos e salvos no próprio agendamento (no status `PENDING` ou `IN_CART`) antes do envio para o checkout.

---

## 2. Modelagem de Dados (Banco de Dados)

Os agendamentos (`schedulings`) e histórico financeiro não podem depender do preço *atual* do instrutor na tabela `users`. Eles precisam armazenar "snapshots" da negociação.

### 2.1. Novos Campos em `Scheduling`
- `lesson_category` (Enum: `A`, `B`, `AB`) -> Qual categoria escolhida.
- `vehicle_ownership` (Enum: `INSTRUCTOR`, `STUDENT`) -> De quem é o veículo.
- `applied_base_price` (Decimal) -> O valor "líquido" que o instrutor solicitou no momento em que o carrinho virou checkout.
- `applied_final_price` (Decimal) -> O valor total que o aluno pagou, incluindo as taxas.

### 2.2. Resiliência a Mudanças de Preço
Se um instrutor alterar seus preços na tela "Meus Preços", **nenhuma aula passada ou aula já paga deve ser afetada**. O uso de campos de snapshot (`applied_base_price`) na tabela de agendamento garante a preservação do histórico financeiro.

---

## 3. Backend e Lógica de Divisão (Split)

O algoritmo *Fee-On-Top* (`PricingService`) não mudará em sua fórmula matemática, mas mudará severamente em sua **entrada de dados**.

### 3.1. Seleção Dinâmica do Preço Base
No use case `CreateCheckoutUseCase`, o backend precisará:
1. Ler o agendamento pendente, checando `lesson_category` e `vehicle_ownership`.
2. Fazer o "lookup" na tabela do instrutor (`users` ou tabela correspondente de perfil) para extrair o preço exato daquela combinação.
3. Validar se a combinação ainda possui um preço válido (se o instrutor não removeu a opção de veículo de aluno, por exemplo).
4. Rodar o `CalculateSplitUseCase` utilizando esse preço específico como o `instructor_base_price`.
5. Salvar esse preço no `Scheduling`.

---

## 4. Integração Financeira (Mercado Pago)

Avaliando a documentação `docs/payments/MP_INTEGRATION.md`, a arquitetura do GoDrive baseada no **Gateway MP** já foi muito bem projetada para suportar essa mudança, com impactos concentrados na pré-geração da preferência.

### 4.1. Checkout Pro
- O processo atual passa o `marketplace_fee` para o Mercado Pago e utiliza o token do vendedor. Isso **não sofre impacto direto** porque o MP não se importa com a origem do valor (se veio da Categoria A ou B), ele só recebe o valor final (`unit_price`) e a taxa (`marketplace_fee`).
- **Aprimoramento Sugerido:** Injetar no `metadata` ou na `description` da *Preference* do Mercado Pago a string indicando a modalidade (ex: "Aula Prática - Categoria B - Veículo do Instrutor"). Isso melhora o extrato do pagador e facilita conciliação manual em disputas (Chargebacks).

### 4.2. Webhooks e Conciliação
- Nenhuma mudança estrutural no `HandlePaymentWebhookUseCase`. Quando o webhook confirma o pagamento (`approved`), o sistema buscará os registros em `payments`, que já terão sido gravados com os valores splitados originais, agnósticos sobre de onde vieram.

### 4.3. Reembolsos
- Sem impacto negativo esperado. Como o `ProcessRefundUseCase` atua em cima da tabela `payments` que possui `platform_fee_amount` e `instructor_amount` consolidados no momento do aceite do pagamento, reversões parciais ou absolutas continuarão matemáticas e isentas a flutuações da tabela de perfis de instrutores.

---

## 5. Aplicativo do Instrutor (Gestão e Agenda)

Como as opções agora ditam diretamente a rotina física e logística do instrutor, isso deve estar claro nas áreas de controle.

### 5.1. Tela `InstructorScheduleScreen`
- Os cards das agendas precisam conter *badges* fortes:
  - `[ Categoria A - Veículo do Aluno ]`
  - `[ Categoria B - Meu Veículo ]`
- É vital que o instrutor saiba no dia se ele precisará se deslocar de Uber até o aluno (se for veículo do aluno) ou se ele deve estar no carro de dupla-empenhagem limpo e abastecido.

### 5.2. Relatórios de Ganhos (`earnings.py` / `InstructorDashboard`)
- No futuro, será extremamente valioso para o instrutor saber se ele lucra mais usando o carro dele ou deixando o aluno usar o carro próprio. O endpoint `/api/v1/instructors/earnings` precisará, posteriormente, agregar esses dados agrupados pela nova coluna `vehicle_ownership`.

---

## 6. Resumo das Tarefas Pendentes (Actionable Items)

1. **Backend / API**:
   - Modificar modelo `Scheduling` (novos campos e enum).
   - Atualizar migrations do banco em Alembic.
   - Alterar lógicas de criação do carrinho (`add_to_cart`) para exigir e armazenar o tipo de aula.
   - Refatorar o `CreateCheckoutUseCase` para aplicar lookup dinâmico de `base_price` ao chamar a `CalculateSplitUseCase`.
2. **Frontend Aluno**:
   - Atualizar a UI do perfil do instrutor para exibir as quatro opções de preço.
   - Criar o seletor modal na hora de reservar o horário.
   - Atualizar UI do Carrinho para exibir as escolhas (Item da Lista).
3. **Frontend Instrutor**:
   - Modificar a visualização do agendamento (cards de horário e detalhes da aula) para exibir a Categoria e Veículo.
4. **MP Integration**:
   - Passar metadata atualizada nas requisições do Gateway `POST /checkout/preferences`.
