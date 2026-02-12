# Planejamento: Home do Instrutor

Este documento detalha as etapas para a implementação da tela inicial do aplicativo do instrutor, seguindo as diretrizes do projeto.

## 1. Visão Geral Visual
A home do instrutor deve fornecer uma visão rápida e clara do seu dia de trabalho e desempenho financeiro.
- **Header:** Saudação personalizada ("Olá, [Nome]!") e ícone de notificações.
- **Passos Rápidos:** Carrossel de tutorial para novos instrutores (ex: completar perfil, configurar agenda, aceitar aulas).
- **Próxima Aula:** Card com detalhes da aula mais próxima, reaproveitando o componente `ScheduleCard.tsx`.
- **Ganhos do Dia:** Resumo financeiro de hoje (total recebido e número de aulas).
- **Avisos:** Seção de comunicados importantes da plataforma.

---

## 2. Etapas de Backend (Novas Funcionalidades)

Para suportar a home, precisaremos adicionar/ajustar alguns endpoints:

### 2.1. Ganhos do Dia
Atualmente o endpoint de ganhos retorna o total acumulado. Precisamos de um filtro por data.
- **Action:** Modificar `GetInstructorEarningsUseCase` ou adicionar `GetDailyEarningsUseCase`.
- **Endpoint:** `GET /api/v1/instructor/earnings/daily`

### 2.2. Próxima Aula
Otimizar a busca pela aula mais próxima que ainda não começou ou está em andamento. Deve retornar os dados no formato `Scheduling` esperado pelo front.
- **Action:** Criar `GetNextClassUseCase` no backend.
- **Endpoint:** `GET /api/v1/instructor/schedule/next`

### 2.3. Avisos (Announcements)
Implementar uma entidade simples para avisos globais ou por tipo de usuário.
- **Action:** Criar entidade `Announcement`, repositório e caso de uso.
- **Endpoint:** `GET /api/v1/shared/announcements?user_type=instructor`

---

## 3. Etapas de Frontend (Mobile)

### 3.1. Camada de Dados (API & Hooks)
- Criar `mobile/src/features/instructor-app/api/homeApi.ts` para centralizar as chamadas.
- Criar `mobile/src/features/instructor-app/hooks/useInstructorHome.ts` usando TanStack Query para gerenciar o estado e cache.
- O hook deve gerenciar as mutações (confirmar, concluir, cancelar, reagendar) necessárias para o `ScheduleCard`.

### 3.2. Componentes (UI)
Organizar em `mobile/src/features/instructor-app/components/home/`:
1. `InstructorWelcomeHeader.tsx`: Reutilizar lógica de `WelcomeHeader` do aluno.
2. `InstructorQuickSteps.tsx`: Tutorial com passos específicos para o instrutor.
3. **Reuso de `ScheduleCard.tsx`**: Integrar o componente existente na seção de "Próxima Aula", passando as props de estado e funções de callback gerenciadas pelo hook da home.
4. `InstructorEarningsSection.tsx`: Exibição visual dos ganhos diários.
5. `InstructorAnnouncementsSection.tsx`: Lista de avisos.

### 3.3. Tela Principal
- Atualizar `mobile/src/features/instructor-app/screens/InstructorHomeScreen.tsx` para compor os novos componentes e integrar com o hook de dados.


---

## 4. Plano de Verificação

1. **Backend:**
   - Testes unitários para os novos Use Cases.
   - Testes de integração para os novos endpoints da API.
2. **Frontend:**
   - Validar renderização dos componentes com dados mockados.
   - Validar integração real com a API.
   - Testar estado de "vazio" (sem aulas hoje, sem avisos).
