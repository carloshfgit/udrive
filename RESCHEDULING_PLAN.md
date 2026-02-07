# RESCHEDULING PLAN - GoDrive (UDrive)

Este documento detalha o plano de implementação para a funcionalidade de reagendamento de aulas, permitindo que alunos solicitem uma nova data/horário e que instrutores aprovem ou recusem tal solicitação.

## 1. Backend (Clean Architecture)

### 1.1 Domínio (Domain Layer)
- **[MODIFY]** `src/domain/entities/scheduling_status.py`: 
    - Adicionar `RESCHEDULE_REQUESTED = "reschedule_requested"` ao enum `SchedulingStatus`.
- **[MODIFY]** `src/domain/entities/scheduling.py`:
    - Adicionar campo `rescheduled_datetime: datetime | None = None`.
    - Adicionar métodos de domínio:
        - `request_reschedule(new_datetime)`: Valida se pode solicitar (ex: status confirmed/pending) e altera para `RESCHEDULE_REQUESTED`.
        - `accept_reschedule()`: Atualiza `scheduled_datetime` com `rescheduled_datetime`, limpa `rescheduled_datetime` e volta status para `CONFIRMED`.
        - `refuse_reschedule()`: Volta status original (preservado em uma lógica simples ou assumindo `CONFIRMED`) e limpa `rescheduled_datetime`.

### 1.2 Infraestrutura (Infrastructure Layer)
- **[MODIFY]** `src/infrastructure/db/models/scheduling_model.py`:
    - Adicionar coluna `rescheduled_datetime` (DateTime com Timezone).
    - Atualizar `to_entity` e `from_entity`.
- **[NEW]** `alembic/versions/xxxx_add_reschedule_fields.py`:
    - Migration para adicionar a coluna e atualizar o tipo enum no PostgreSQL.

### 1.3 Aplicação (Application Layer - Use Cases)
- **[NEW]** `src/application/use_cases/scheduling/request_reschedule_use_case.py`:
    - Valida disponibilidade do instrutor para a nova data.
    - Atualiza o agendamento para `RESCHEDULE_REQUESTED`.
- **[NEW]** `src/application/use_cases/scheduling/respond_reschedule_use_case.py`:
    - Recebe a decisão do instrutor (aceitar/recusar).
    - Executa a transição de estado correspondente.

### 1.4 Interface (API Layer)
- **[MODIFY]** `src/interface/api/v1/student/lessons.py`:
    - Adicionar endpoint `POST /lessons/{id}/request-reschedule`.
- **[MODIFY]** `src/interface/api/v1/instructor/schedule.py`:
    - Adicionar endpoint `POST /schedule/{id}/respond-reschedule`.

---

## 2. Mobile (Feature-Based Architecture)

### 2.1 API e Hooks (Shared)
- **[MODIFY]** `src/features/shared-features/scheduling/api/schedulingApi.ts` & `src/features/instructor-app/api/scheduleApi.ts`:
    - Atualizar tipos `Scheduling` e `SchedulingStatus`.
    - Adicionar funções de chamada para os novos endpoints de reagendamento.
- **[MODIFY]** `src/features/shared-features/scheduling/hooks/useLessonDetails.ts`:
    - Adicionar mutação `requestReschedule`.

### 2.2 Aplicativo do Aluno (Student App)
- **[MODIFY]** `src/features/student-app/scheduling/screens/LessonDetailsScreen.tsx`:
    - Adicionar botão **"Reagendar Aula"** (visível para aulas não concluídas/canceladas).
    - Integrar com o fluxo de seleção de data (reutilizar `SelectDateTimeScreen` se possível ou abrir modal com calendário).
    - Exibir Badge/Status visual de **"Reagendamento Pendente"** quando `status === 'reschedule_requested'`.
    - Lógica para exibir mensagem caso o reagendamento anterior tenha sido recusado (opcional, baseado em campos extras ou apenas resetando o fluxo).

### 2.3 Aplicativo do Instrutor (Instructor App)
- **[MODIFY]** `src/features/instructor-app/screens/InstructorScheduleScreen.tsx`:
    - No `ScheduleCard`, se o status for `reschedule_requested`:
        - Exibir label **"Reagendamento Solicitado"** em destaque (ex: cor amarela/laranja).
        - Substituir botões padrão por um botão **"Ver Detalhes do Reagendamento"**.
- **[NEW]** `src/features/instructor-app/screens/RescheduleDetailsScreen.tsx`:
    - Tela de comparação de horários.
    - Exibir:
        - Horário Atual: `scheduled_datetime`.
        - Horário Solicitado: `rescheduled_datetime`.
    - Botões de ação:
        - **Aceitar Reagendamento**: Chama API de resposta positiva.
        - **Recusar Reagendamento**: Chama API de resposta negativa.
        - **Chat com Aluno**: Atalho para a funcionalidade de chat.
- **[MODIFY]** `src/features/instructor-app/navigation/InstructorScheduleStack.tsx`:
    - Registrar a nova tela `RescheduleDetailsScreen`.

---

## 3. Plano de Verificação

### 3.1 Testes Automatizados (Backend)
- Unitários para os novos métodos da entidade `Scheduling`.
- Integração para os Use Cases `RequestReschedule` e `RespondReschedule`.

### 3.2 Verificação Manual (Frontend)
1. Aluno solicita reagendamento em uma aula confirmada.
2. Verificar se o card no app do aluno mudou para "Pendente".
3. Abrir app do instrutor e localizar o card com "Reagendamento Solicitado".
4. Abrir detalhes do reagendamento e clicar em "Aceitar".
5. Verificar se ambos os apps mostram agora a nova data e o status "Confirmado" (sem o label de reagendamento).
6. Repetir o fluxo, mas clicando em "Recusar" e verificar a manutenção do horário original.
