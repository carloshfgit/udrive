# Planejamento de Implementação: Home do Aluno

Este documento detalha as etapas lógicas e técnicas para a implementação da tela inicial do aluno no app GoDrive, seguindo as diretrizes de Clean Architecture (Backend) e Feature-Based Architecture (Mobile).

## 1. Análise de Requisitos e Backend

Com base na descrição visual, os seguintes dados são necessários:
- **Saudação personalizada:** Nome do aluno (disponível em `GET /api/v1/student/profile`).
- **Notificações:** Icone de sino que abre modal com lista de notificações pendentes (necessário criar backend).
- **Tutorial de passos rápidos:** Podemos deixar fixo por enquanto, depois implementamos o backend.
- **Próxima aula:** Detalhes do agendamento confirmado mais próximo (disponível em `GET /api/v1/student/lessons`).
- **Barra de progresso:** Aulas concluídas vs numero fixo de 10 aulas (disponível em `GET /api/v1/student/profile`).
- **Avisos:** Mensagens administrativas ou globais (necessário criar backend).

---

## 2. Etapas Lógicas de Backend

### Fase 1: Entidades e Persistência
1.  **Notificações & Avisos:**
    - Criar entidades de domínio `Announcement` e `Notification`.
    - Implementar modelos SQLAlchemy e migrações Alembic correspondentes.
2.  **Perfil do Aluno:**
    - Adicionar campo `has_seen_tutorial` ao modelo `StudentProfile` para persistir o progresso do onboarding.

### Fase 2: Casos de Uso (Application Layer)
1.  Implementar `GetStudentAnnouncements` para filtrar avisos relevantes.
2.  Implementar `GetStudentNotifications` para listar alertas do sistema.
3.  Futuramente implementar `MarkTutorialAsSeen` para atualizar o estado do aluno.

### Fase 3: Interface API
1.  Criar `router` em `interface/api/routers/shared/announcements.py`.
2.  Criar `router` em `interface/api/routers/shared/notifications.py`.
3.  Expor novos campos e endpoints na documentação OpenAPI.

---

## 3. Etapas de Implementação Mobile

### Fase 4: Camada de Dados (API & Hooks)
1.  Configurar `homeApi.ts` dentro de `features/student-app/home/api/`.
2.  Criar hooks `useHomeData` utilizando TanStack Query para gerenciar cache e estados de loading/error.

### Fase 5: Componentes de UI (Atomic Design)
Implementar componentes isolados em `features/student-app/home/components/`:
- **WelcomeHeader:** Header com nome, avatar e ícone de sino (c/ badge de notificação).
- **QuickStepsTutorial:** Lista horizontal ou grid de cards rápidos (onboarding).
- **NextClassCard:** Card destacado com data, hora, instrutor e local da aula. (reaproveitar card de agendamentos)
- **LessonProgressBar:** Barra visual do progresso.
- **AnnouncementsSection:** Feed vertical de avisos com cores temáticas.

### Fase 6: Montagem e Integração
1.  Refatorar `HomeScreen.tsx` para compor as seções.
2.  Implementar lógica de "Next Class" filtrando a lista de agendamentos do backend.
3.  Adicionar animações sutis de entrada com `react-native-reanimated` (opcional, mas recomendado).

---

## 4. Plano de Verificação

### Backend
- Testes unitários para lógica de filtro de avisos (`pytest`).
- Validação dos endpoints via Swagger/Insomnia.

### Mobile
- Teste visual de responsividade em diferentes tamanhos de tela.
- Simulação de estados: "Sem aulas agendadas", "Tutorial concluído", "Erro de conexão".
- Verificação do cálculo da barra de progresso (ex: 3/10 = 30%).

---

## 5. Próximos Passos (Workflow)
1.  [ ] Executar migrações de backend.
2.  [ ] Criar os novos endpoints.
3.  [ ] Implementar os componentes mobile base.
4.  [ ] Realizar a integração final.
