# ADMIN PANEL PLAN — GoDrive

Plano geral por fases para o painel administrativo dedicado do GoDrive.
O painel será um projeto **frontend React/Next.js separado** que consome a API existente (`/api/v1/admin/*`).

---

## Diagnóstico do Backend Atual

### ✅ O que já existe

| Recurso | Status | Detalhes |
|---------|--------|----------|
| Entidade `User` | ✅ Completo | `id`, `email`, `full_name`, `user_type` (student/instructor/admin), `is_active`, `is_verified`, `phone`, `cpf`, `birth_date` |
| Entidade `Scheduling` | ✅ Completo | 6 status (`pending`, `confirmed`, `cancelled`, `completed`, `reschedule_requested`, `disputed`), regras de cancelamento/reagendamento/disputa já implementadas |
| Entidade `Dispute` | ✅ Completo | Status (`open`, `under_review`, `resolved`), 3 tipos de resolução (`favor_instructor`, `favor_student`, `rescheduled`) |
| Endpoints Admin — Disputas | ✅ 4 endpoints | `GET /disputes`, `GET /disputes/{id}`, `POST /disputes/{id}/resolve`, `PATCH /disputes/{id}/status` |
| Guard `require_admin` | ✅ Funcional | `CurrentAdmin` dependency no FastAPI |
| JWT Auth | ✅ Funcional | Access Token (15min) + Refresh Token (7 dias) |
| SQLAdmin (legado) | ✅ Existe | Interface admin básica via SQLAlchemy Admin (será substituída por este painel) |

### ❌ O que falta no Backend (a criar)

| Recurso | Tipo | Endpoints Necessários |
|---------|------|-----------------------|
| **Admin Users** | Routers + Use Cases | `GET /admin/users` (listar com filtro/paginação), `GET /admin/users/{id}` (detalhes com perfil), `PATCH /admin/users/{id}/status` (ativar/desativar), `GET /admin/users/search?q=` (busca por nome/email/cpf) |
| **Admin Schedulings** | Routers + Use Cases | `GET /admin/schedulings` (listar com filtros: status, data, user), `GET /admin/schedulings/{id}` (detalhes completos com nomes e pagamento), `PATCH /admin/schedulings/{id}/cancel` (cancelar como admin) |
| **IUserRepository** | Métodos novos | `list_all(filters, limit, offset)`, `count_all(filters)`, `search(query)` |
| **ISchedulingRepository** | Métodos novos | `list_all(filters, limit, offset)`, `count_all(filters)` |

---

## Estrutura de Pastas do Frontend

```
admin/
├── public/
├── src/
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                 # Layout global (sidebar + topbar)
│   │   ├── page.tsx                   # Dashboard (placeholder → futuro KPIs)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── users/
│   │   │   ├── page.tsx               # Lista de usuários
│   │   │   └── [id]/
│   │   │       └── page.tsx           # Detalhes do usuário
│   │   ├── schedulings/
│   │   │   ├── page.tsx               # Lista de agendamentos
│   │   │   └── [id]/
│   │   │       └── page.tsx           # Detalhes do agendamento
│   │   └── disputes/
│   │       ├── page.tsx               # Lista de disputas
│   │       └── [id]/
│   │           └── page.tsx           # Detalhes + resolução
│   ├── components/
│   │   ├── layout/                    # Sidebar, Topbar, BreadCrumbs
│   │   ├── ui/                        # Botões, Inputs, Modais, Badge, Table
│   │   └── shared/                    # StatusBadge, Pagination, SearchInput, Filters
│   ├── hooks/                         # useAuth, useUsers, useSchedulings, useDisputes
│   ├── lib/
│   │   ├── api.ts                     # Instância Axios configurada
│   │   ├── auth.ts                    # JWT helpers (refresh, interceptors)
│   │   └── query-client.ts            # TanStack Query config
│   ├── services/                      # Funções de API organizadas por recurso
│   │   ├── auth.service.ts
│   │   ├── users.service.ts
│   │   ├── schedulings.service.ts
│   │   └── disputes.service.ts
│   ├── types/                         # TypeScript types/interfaces
│   │   ├── user.ts
│   │   ├── scheduling.ts
│   │   ├── dispute.ts
│   │   └── api.ts                     # PaginatedResponse, ApiError, etc.
│   └── styles/
│       └── globals.css                # Design tokens, variáveis CSS
├── .env.local
├── next.config.js
├── tsconfig.json
└── package.json
```

---

## Fases de Desenvolvimento

### FASE 0 — Preparação do Backend (Pré-requisito)
> **Foco:** Garantir que o backend tenha tudo que o frontend precisa consumir.

**Etapa 0.1 — Endpoints Admin de Usuários**
- Criar `backend/src/interface/api/routers/admin/users.py`
- Criar use cases: `ListUsersUseCase`, `GetUserDetailsUseCase`, `ToggleUserStatusUseCase`, `SearchUsersUseCase`
- Adicionar métodos `list_all()`, `count_all()`, `search()` ao `IUserRepository` e implementação concreta
- Registrar no `admin/__init__.py`

**Etapa 0.2 — Endpoints Admin de Agendamentos**
- Criar `backend/src/interface/api/routers/admin/schedulings.py`
- Criar use cases: `ListAllSchedulingsUseCase`, `GetSchedulingDetailsUseCase`, `AdminCancelSchedulingUseCase`
- Adicionar métodos `list_all()`, `count_all()` ao `ISchedulingRepository` e implementação concreta
- Registrar no `admin/__init__.py`

**Etapa 0.3 — CORS e Auth para o Admin Panel**
- Adicionar origin do admin panel na config CORS (`http://localhost:3000`)
- Verificar que o login via JWT funciona para `user_type=admin` e retorna o tipo no token
- Endpoint de login já existente (`/api/v1/auth/login`) deve funcionar para admin

---

### FASE 1 — Scaffold e Autenticação do Frontend
> **Foco:** Criar o projeto Next.js, sistema de design base e fluxo de auth.

**Etapa 1.1 — Inicialização do Projeto**
- Criar projeto Next.js (App Router, TypeScript, ESLint)
- Configurar dependências: `axios`, `@tanstack/react-query`, `react-icons` (ou `lucide-react`)
- Configurar `.env.local` com `NEXT_PUBLIC_API_URL`
- Configurar Axios com interceptors (access token, refresh automático)

**Etapa 1.2 — Sistema de Design Base**
- Criar `globals.css` com variáveis CSS (cores, tipografia, espaçamentos)
- Definir paleta de cores para dark mode (padrão de admin panels modernos)
- Configurar fonte (Google Fonts — ex: Inter)
- Criar componentes base: `Button`, `Input`, `Badge`, `Card`, `Modal`

**Etapa 1.3 — Layout e Autenticação**
- Criar `Sidebar` com navegação (Dashboard, Usuários, Agendamentos, Disputas)
- Criar `TopBar` com info do admin logado e logout
- Implementar tela de Login com validação
- Implementar `AuthProvider` / `useAuth` com controle de sessão JWT
- Implementar middleware de proteção de rotas (redirecionar para `/login` se não autenticado)

---

### FASE 2 — Feature: Gestão de Usuários
> **Foco:** CRUD completo de visualização e gerenciamento de usuários.

**Etapa 2.1 — Listagem de Usuários**
- Tabela paginada com colunas: Nome, Email, Tipo, Status, Data de Cadastro
- Filtros: por tipo (student/instructor), por status (ativo/inativo), busca por texto
- Badges coloridos para tipo e status
- Server-side pagination via query params

**Etapa 2.2 — Detalhes do Usuário**
- Página de detalhes com dados completos (nome, email, cpf, telefone, data nascimento)
- Seção de perfil (instrutor: veículo, preços, avaliações | aluno: agendamentos)
- Histórico de agendamentos do usuário (tabela resumida)
- Ação: botão Ativar/Desativar conta

---

### FASE 3 — Feature: Gestão de Agendamentos
> **Foco:** Visualização e gerenciamento de todos os agendamentos do sistema.

**Etapa 3.1 — Listagem de Agendamentos**
- Tabela paginada: Aluno, Instrutor, Data/Hora, Status, Valor, Categoria
- Filtros: por status (pending, confirmed, cancelled, completed, disputed), por data (range picker), por usuário
- Badges coloridos por status
- Server-side pagination

**Etapa 3.2 — Detalhes do Agendamento**
- Informações completas: aluno, instrutor, data/hora, duração, preço base e final, categoria, veículo
- Timeline de eventos (criação, confirmação, início, conclusão/cancelamento)
- Status do pagamento associado
- Ações: cancelar como admin (com motivo), link para disputa vinculada (se existir)

---

### FASE 4 — Feature: Gestão de Disputas
> **Foco:** Consumir os endpoints admin de disputas já existentes.

**Etapa 4.1 — Listagem de Disputas**
- Tabela paginada: Motivo, Aluno, Status, Data de Abertura
- Filtros: por status (open, under_review, resolved)
- Indicador de prioridade visual (open = urgente)

**Etapa 4.2 — Detalhes + Mediação**
- Detalhes da disputa: motivo, descrição do aluno, telefone/email de contato
- Dados do agendamento vinculado (aluno, instrutor, data/hora, valor)
- Botão "Iniciar Análise" (OPEN → UNDER_REVIEW)
- Formulário de resolução:
  - Resolução: Favor Instrutor | Favor Aluno | Reagendamento
  - Se Favor Aluno: selecionar tipo de reembolso (total/parcial)
  - Se Reagendamento: date picker para nova data
  - Notas internas do admin (obrigatório)

---

### FASE 5 — Polimento e Qualidade
> **Foco:** Refinar UX, performance e preparar para produção.

**Etapa 5.1 — UX e Feedback**
- Loading states (skeletons) em todas as tabelas
- Toasts de sucesso/erro para ações
- Confirmação em ações destrutivas (modais)
- Empty states informativos

**Etapa 5.2 — Performance e SEO**
- Prefetch de queries com TanStack Query
- Otimistic updates onde aplicável
- Meta tags e títulos descritivos por página

**Etapa 5.3 — Docker e Deploy**
- Adicionar serviço `admin` ao `docker-compose.yml`
- Configurar Dockerfile de produção para o Next.js
- Verificação de build de produção

---

## Fases Futuras (fora do escopo atual)

| Fase | Feature | Descrição |
|------|---------|-----------|
| 6 | KPIs e Métricas | Cards com total de usuários, agendamentos, disputas abertas, receita |
| 7 | Gráficos BI | Gráficos com Chart.js/Recharts — agendamentos por dia, receita por mês |
| 8 | Suporte ao Cliente | Chat com usuários, tickets de suporte, base de conhecimento |

---

## Princípios e Boas Práticas

1. **Separação de responsabilidades**: Services (API calls) → Hooks (state management) → Components (UI)
2. **TypeScript Strict Mode**: Toda a base de código tipada, interfaces para todos os modelos
3. **TanStack Query**: Cache e sincronização de dados do servidor, sem estado global desnecessário
4. **Componentes reutilizáveis**: DataTable, StatusBadge, Pagination, SearchInput, FilterBar
5. **CSS Variables**: Design tokens centralizados para fácil customização e tema
6. **Error Boundaries**: Tratamento de erros em nível de componente
7. **Responsive**: Layout adaptável (sidebar colapsável em telas menores)
