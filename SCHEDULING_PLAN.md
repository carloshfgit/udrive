# M8.2 - Gestão de Agenda do Instrutor

> Plano de implementação detalhado, dividido em etapas sequenciais.

---

## Visão Geral

Transformar o placeholder atual em duas telas funcionais:
1. **InstructorScheduleScreen** - Calendário com aulas do instrutor
2. **InstructorAvailabilityScreen** - Configuração de horários disponíveis

---

## Etapa 1: Backend - Endpoint de Listagem de Disponibilidade ✅

**Objetivo:** Adicionar endpoint GET `/instructor/availability` para listar slots.

**Arquivos a modificar:**
- `backend/src/interface/api/routers/instructor/availability.py`

**Mudanças:**
- Adicionar endpoint GET que usa `availability_repo.list_by_instructor()`
- Retornar `AvailabilityListResponse` com lista de slots

**Verificação:**
```bash
curl -X GET http://localhost:8000/api/v1/instructor/availability \
  -H "Authorization: Bearer <token>"
```

---

## Etapa 2: Backend - Endpoint de Agenda por Data ✅

**Objetivo:** Adicionar endpoint GET `/instructor/schedule/by-date` para buscar aulas de uma data.

**Arquivos a modificar:**
- `backend/src/interface/api/routers/instructor/schedule.py`
- `backend/src/infrastructure/repositories/scheduling_repository_impl.py`
- `backend/src/domain/interfaces/scheduling_repository.py`

**Mudanças:**
- Adicionar método `list_by_instructor_and_date(instructor_id, date)` no repositório
- Adicionar endpoint GET que recebe query param `date` (YYYY-MM-DD)

**Verificação:**
```bash
curl -X GET "http://localhost:8000/api/v1/instructor/schedule/by-date?date=2026-02-03" \
  -H "Authorization: Bearer <token>"
```

---

## Etapa 3: Mobile - API Layer ✅

**Objetivo:** Criar funções de comunicação com os novos endpoints.

**Arquivos a criar:**
- `mobile/src/features/instructor-app/api/scheduleApi.ts`

**Funções:**
```typescript
// Availability
getAvailabilities(): Promise<AvailabilityListResponse>
createAvailability(data): Promise<Availability>
deleteAvailability(id): Promise<void>

// Schedule
getScheduleByDate(date): Promise<SchedulingListResponse>
confirmScheduling(id): Promise<Scheduling>
completeScheduling(id): Promise<Scheduling>
```

**Tipos a definir:**
- `Availability`, `AvailabilityListResponse`
- `Scheduling`, `SchedulingListResponse`

---

## Etapa 4: Mobile - Hooks TanStack Query ✅

**Objetivo:** Criar hooks reativos para gerenciamento de estado do servidor.

**Arquivos a criar:**
- `mobile/src/features/instructor-app/hooks/useInstructorAvailability.ts`
- `mobile/src/features/instructor-app/hooks/useInstructorSchedule.ts`

**Hooks de Availability:**
- `useAvailabilities()` → Query
- `useCreateAvailability()` → Mutation
- `useDeleteAvailability()` → Mutation

**Hooks de Schedule:**
- `useScheduleByDate(date)` → Query
- `useConfirmScheduling()` → Mutation
- `useCompleteScheduling()` → Mutation

---

## Etapa 5: Mobile - Tela de Disponibilidade ✅

**Objetivo:** Criar nova tela para configurar horários disponíveis.

**Arquivos a criar:**
- `mobile/src/features/instructor-app/screens/InstructorAvailabilityScreen.tsx`

**Arquivos a modificar:**
- `mobile/src/features/instructor-app/screens/index.ts` (exportar)

**UI:**
- Header com título e botão voltar
- Lista agrupada por dia da semana (0-6)
- Cards de slot: horário início-fim, botão remover
- BottomSheet para adicionar novo slot
- Empty state quando não há configuração

---

## Etapa 6: Mobile - Tela de Agenda (Reescrita) ✅

**Objetivo:** Substituir placeholder por tela funcional com calendário.

**Arquivos a modificar:**
- `mobile/src/features/instructor-app/screens/InstructorScheduleScreen.tsx`

**UI:**
- Header com título e botão "Horários"
- Calendário horizontal (semana) ou mensal simples
- Lista de aulas do dia selecionado
- Cards de aula: horário, aluno, status, ações
- Loading state e Empty state

**Ações disponíveis:**
- Selecionar dia no calendário
- Confirmar aula pendente
- Marcar aula como concluída

---

## Etapa 7: Mobile - Navegação ✅

**Objetivo:** Configurar navegação entre Agenda e Disponibilidade.

**Arquivos a criar:**
- `mobile/src/features/instructor-app/navigation/InstructorScheduleStack.tsx`

**Arquivos a modificar:**
- `mobile/src/features/instructor-app/navigation/InstructorTabNavigator.tsx`

**Estrutura:**
```
InstructorSchedule (Tab)
  └── InstructorScheduleStack (Stack Navigator)
       ├── ScheduleMain → InstructorScheduleScreen
       └── Availability → InstructorAvailabilityScreen
```

---

## Ordem de Execução Recomendada

| # | Etapa | Dependência |
|---|-------|-------------|
| 1 | Backend - Listagem Availability | - |
| 2 | Backend - Agenda por Data | - |
| 3 | Mobile - API Layer | Etapas 1-2 |
| 4 | Mobile - Hooks | Etapa 3 |
| 5 | Mobile - Tela Disponibilidade | Etapa 4 |
| 6 | Mobile - Tela Agenda | Etapas 4-5 |
| 7 | Mobile - Navegação | Etapas 5-6 |

---

## Checklist de Verificação Final

- [ ] Endpoint GET availability retorna lista correta
- [ ] Endpoint GET schedule/by-date filtra por data
- [ ] Tela de disponibilidade permite adicionar/remover slots
- [ ] Tela de agenda mostra calendário e lista de aulas
- [ ] Navegação entre telas funciona corretamente
- [ ] Identidade visual consistente (cores, cards, ícones)
- [ ] Estados de loading e empty implementados
