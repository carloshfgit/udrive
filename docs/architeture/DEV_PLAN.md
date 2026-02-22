# Plano de Desenvolvimento - GoDrive (UDrive)

> **Marketplace SaaS** para conectar alunos a instrutores de direção independentes no Brasil.

---

## Fase 1: Fundação e Infraestrutura Base

Objetivo: Estabelecer a base técnica do projeto, configurando o ambiente de desenvolvimento e a estrutura arquitetural conforme as diretrizes.

### Etapa 1.1: Configuração do Ambiente de Desenvolvimento

| Item | Descrição |
|------|-----------|
| Docker & Docker Compose | Configurar containers para desenvolvimento local (PostgreSQL + PostGIS, Redis, Backend) |
| Repositório Git | Inicializar repositório com estrutura de branches (main, develop, feature/*) |
| Linters & Formatters | Configurar Ruff (Python) e ESLint + Prettier (TypeScript) |
| Pre-commit Hooks | Garantir padrões de código antes de cada commit |

### Etapa 1.2: Estrutura do Backend (Clean Architecture)

```text
backend/src/
├── domain/
│   ├── entities/
│   └── interfaces/
├── application/
│   └── use_cases/
├── infrastructure/
│   ├── db/
│   ├── repositories/
│   ├── external/
│   └── tasks/
└── interface/
    ├── api/
    └── websockets/
```

- [x] Criar estrutura de pastas conforme Clean Architecture
- [x] Configurar FastAPI com estrutura modular
- [x] Configurar SQLAlchemy 2.0+ com suporte a async
- [x] Configurar Alembic para migrations

### Etapa 1.3: Estrutura do Mobile (Feature-Based Architecture)

```text
mobile/src/
├── app/
├── features/
│   ├── auth/
│   ├── map/
│   └── scheduling/
├── shared/
└── lib/
```

- [x] Inicializar projeto Expo com TypeScript (Strict Mode)
- [x] Configurar NativeWind (TailwindCSS)
- [x] Configurar Zustand para estado global
- [x] Configurar TanStack Query v5+ com Axios

### Etapa 1.4: Banco de Dados

- [x] Configurar PostgreSQL 15+ com extensão PostGIS
- [x] Definir pool de conexões (pool_size=20, max_overflow=10)
- [x] Criar migration inicial com índices críticos (GIST para geometria)
- [x] Testar rollback de migrations

---

## Fase 2: Autenticação e Gerenciamento de Usuários

Objetivo: Implementar sistema de autenticação seguro e completo com suporte a diferentes tipos de usuários.

### Etapa 2.1: Entidades e Interfaces (Domain Layer)

- [x] Criar entidade `User` (Aluno, Instrutor, Admin)
- [x] Criar entidade `RefreshToken`
- [x] Definir interface `IUserRepository`
- [x] Definir interface `IAuthService`
- [x] Criar exceções de domínio (`UserNotFoundException`, `InvalidCredentialsException`)

### Etapa 2.2: Casos de Uso (Application Layer)

- [x] `register_user.py` - Cadastro de novos usuários
- [x] `login_user.py` - Autenticação com JWT
- [x] `refresh_token.py` - Rotação de refresh tokens
- [x] `reset_password.py` - Recuperação de senha
- [x] `logout_user.py` - Invalidação de tokens

### Etapa 2.3: Implementação (Infrastructure Layer)

- [x] Modelo SQLAlchemy para `User` e `RefreshToken`
- [x] Implementar `UserRepository`
- [x] Configurar JWT (python-jose/authlib)
  - Access Token: 15 minutos
  - Refresh Token: 7 dias com rotação
- [x] Hash de senhas com bcrypt/argon2

### Etapa 2.4: Endpoints REST (Interface Layer)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/auth/register` | POST | Cadastro |
| `/auth/login` | POST | Login |
| `/auth/refresh` | POST | Renovar token |
| `/auth/logout` | POST | Logout |
| `/auth/forgot-password` | POST | Solicitar reset |
| `/auth/reset-password` | POST | Reset de senha |

### Etapa 2.5: Rate Limiting & Segurança

- [x] Configurar `slowapi` com limites:
  - Login: 5 tentativas/min por IP
  - API geral: 100 req/min por usuário
  - Endpoints públicos: 30 req/min por IP
- [x] Headers de segurança (HSTS, X-Frame-Options, X-Content-Type-Options)
- [x] CORS restrito a domínios conhecidos

### Etapa 2.6: Mobile - Feature Auth

- [x] Tela de Login
- [x] Tela de Cadastro (Aluno/Instrutor)
- [x] Tela de Recuperação de Senha
- [x] Armazenamento seguro com `expo-secure-store`
- [x] Hook `useAuth` para gerenciamento de estado

---

## Fase 3: Perfis e Geolocalização

Objetivo: Implementar perfis de usuários e sistema de geolocalização para busca de instrutores.

### Etapa 3.1: Entidades e Interfaces (Domain Layer)

- [x] Criar entidade `InstructorProfile`
- [x] Criar entidade `StudentProfile`
- [x] Criar entidade `Location` (com suporte a geometria PostGIS)
- [x] Definir interface `IInstructorRepository`
- [x] Definir interface `ILocationService`
- [x] Exceção `DriverNotFoundException`

### Etapa 3.2: Casos de Uso (Application Layer)

- [x] `update_instructor_profile.py`
- [x] `update_student_profile.py`
- [x] `search_instructors_by_location.py` (raio configurável, padrão 10km)
- [x] `update_instructor_location.py`
- [x] `get_nearby_instructors.py`

### Etapa 3.3: Implementação (Infrastructure Layer)

- [x] Modelos SQLAlchemy com colunas PostGIS (Geometry)
- [x] Índice GIST para colunas de geometria
- [x] Cache Redis para busca de instrutores
- [x] Implementar repositórios com queries espaciais

### Etapa 3.4: Endpoints REST (Interface Layer)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/instructors/profile` | GET/PUT | Gerenciar perfil |
| `/instructors/location` | PUT | Atualizar localização |
| `/instructors/search` | GET | Buscar por proximidade |
| `/students/profile` | GET/PUT | Gerenciar perfil |

### Etapa 3.5: Mobile - Features Map & Profiles

- [x] Integrar `react-native-maps`
- [x] Tela de Mapa com marcadores de instrutores
- [x] Tela de Perfil do Instrutor (visualização)
- [x] Tela de Edição de Perfil (Instrutor)
- [x] Tela de Perfil do Aluno
- [x] Implementar updates de posição:
  - A cada **5s** em movimento
  - A cada **30s** parado
- [x] Otimização com `useCallback` e `useMemo` para listas

---

## Fase 4: Sistema de Agendamento

Objetivo: Implementar o core do negócio - agendamento de aulas entre alunos e instrutores.

### Etapa 4.1: Entidades e Interfaces (Domain Layer)

- [x] Criar entidade `Scheduling` (Agendamento)
- [x] Criar entidade `Availability` (Disponibilidade do Instrutor)
- [x] Definir interface `ISchedulingRepository`
- [x] Definir interface `IAvailabilityRepository`
- [x] Exceções de domínio (`SchedulingConflictException`, `UnavailableSlotException`)

### Etapa 4.2: Casos de Uso (Application Layer)

- [x] `create_scheduling.py` - Criar agendamento
- [x] `cancel_scheduling.py` - Cancelar com regras:
  - \> 24h: reembolso 100%
  - < 24h: multa 50%
- [x] `confirm_scheduling.py` - Confirmação do instrutor
- [x] `complete_scheduling.py` - Marcar aula como concluída
- [x] `list_user_schedulings.py` - Histórico
- [x] `manage_availability.py` - CRUD de disponibilidade

### Etapa 4.3: Implementação (Infrastructure Layer)

- [x] Modelos SQLAlchemy para `Scheduling` e `Availability`
- [x] Índices em `user_id`, `created_at`, campos de status
- [x] Implementar repositórios
- [x] Migrations com padrão de nomenclatura

### Etapa 4.4: Endpoints REST (Interface Layer)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/schedulings` | POST | Criar agendamento |
| `/schedulings` | GET | Listar agendamentos |
| `/schedulings/{id}` | GET | Detalhes |
| `/schedulings/{id}/cancel` | POST | Cancelar |
| `/schedulings/{id}/confirm` | POST | Confirmar |
| `/schedulings/{id}/complete` | POST | Concluir |
| `/availability` | GET/POST/PUT/DELETE | CRUD disponibilidade |

### Etapa 4.5: Mobile - Feature Scheduling

- [x] Tela de Calendário de Disponibilidade (Instrutor)
- [x] Tela de Busca e Agendamento (Aluno)
- [x] Tela de Detalhes do Agendamento
- [x] Componente de Confirmação/Cancelamento
- [x] Lista de Agendamentos (histórico)
- [x] Hooks com TanStack Query para cache

---

## Fase 5: Sistema Financeiro e Pagamentos

Objetivo: Implementar integração com Mercado Pago para pagamentos com split atômico.

### Etapa 5.1: Entidades e Interfaces (Domain Layer)

- [x] Criar entidade `Payment`
- [x] Criar entidade `Transaction`
- [x] Definir interface `IPaymentGateway`
- [x] Definir interface `ITransactionRepository`
- [x] Exceções (`PaymentFailedException`, `RefundException`)

### Etapa 5.2: Casos de Uso (Application Layer)

- [x] `process_payment.py` - Processar pagamento com split atômico
- [x] `calculate_split.py` - Calcular divisão (instrutor + plataforma)
- [x] `process_refund.py` - Reembolso conforme regras
- [x] `get_payment_history.py` - Histórico financeiro
- [x] `connect_mercadopago_account.py` - Onboarding Mercado Pago

### Etapa 5.3: Implementação (Infrastructure Layer)

- [x] Modelos SQLAlchemy para `Payment` e `Transaction`
- [x] Integração Mercado Pago Checkout Pro para split payments
- [x] **Split atômico** na transação (não acumular saldo)
- [x] Webhook handlers para Mercado Pago
- [x] Tasks Celery para retry de webhooks

### Etapa 5.4: Endpoints REST (Interface Layer)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/payments/checkout` | POST | Iniciar pagamento |
| `/payments/history` | GET | Histórico |
| `/payments/webhook` | POST | Webhook Mercado Pago |
| `/instructors/mercadopago/connect` | POST | Onboarding Mercado Pago |
| `/instructors/earnings` | GET | Ganhos do instrutor |

### Etapa 5.5: Mobile - Feature Payments

- [x] Tela de Checkout
- [x] Componente de Cartão (Mercado Pago SDK (Checkout Pro))
- [x] Tela de Histórico Financeiro (Instrutor)
- [x] Tela de Extratos (Aluno)
- [x] Onboarding Mercado Pago (WebView)

---

## Fase 6: Notificações e Comunicação em Tempo Real

Objetivo: Implementar notificações push e comunicação via WebSockets.

### Etapa 6.1: Infraestrutura de Notificações

- [ ] Configurar Celery + Redis para tasks assíncronas
- [ ] Estrutura de tasks:
  ```text
  infrastructure/tasks/
  ├── celery_app.py
  ├── notifications.py
  └── reports.py
  ```

### Etapa 6.2: Casos de Uso (Application Layer)

- [ ] `send_push_notification.py`
- [ ] `send_email_notification.py`
- [ ] `broadcast_instructor_update.py`

### Etapa 6.3: WebSockets (Interface Layer)

- [ ] Gerenciador de conexões WebSocket
- [ ] Canal para atualizações de localização em tempo real
- [ ] Canal para status de agendamento
- [ ] PubSub com Redis

### Etapa 6.4: Mobile - Notificações

- [ ] Configurar Expo Notifications
- [ ] Handlers para notificações push
- [ ] Conexão WebSocket para tempo real
- [ ] Indicadores de status na UI

---

## Fase 7: Funcionalidades Avançadas e Dashboards

Objetivo: Implementar recursos avançados e interfaces de administração.

### Etapa 7.1: Casos de Uso Adicionais

- [ ] `generate_instructor_report.py` - Relatórios financeiros
- [ ] `export_user_data.py` - Conformidade LGPD
- [ ] `delete_user_data.py` - Direito ao esquecimento (LGPD)
- [ ] `get_platform_metrics.py` - Métricas para admin

### Etapa 7.2: Endpoints Admin

- [ ] Dashboard de métricas da plataforma
- [ ] Gerenciamento de usuários
- [ ] Relatórios financeiros
- [ ] Endpoints LGPD

### Etapa 7.3: Mobile - Funcionalidades Extras

- [ ] Avaliações e reviews de instrutores
- [ ] Chat in-app (aluno ↔ instrutor)
- [ ] Tela de Configurações
- [ ] Exportar/Excluir dados (LGPD)

---

## Fase 8: Testes e Qualidade

Objetivo: Garantir cobertura de testes e qualidade do código.

### Etapa 8.1: Testes Backend (pytest)

- [ ] Testes unitários para Domain Layer (entidades, regras)
- [ ] Testes unitários para Application Layer (casos de uso)
- [ ] Testes de integração para Infrastructure Layer
- [ ] Fixtures em `conftest.py`
- [ ] Mocks apenas para I/O externo (Mercado Pago, APIs)

### Etapa 8.2: Testes Mobile (Jest)

- [ ] Testes unitários para hooks
- [ ] Testes de componentes
- [ ] Snapshot tests para UI
- [ ] Testes de integração com React Query

### Etapa 8.3: Cobertura e Métricas

- [ ] Meta: > 80% de cobertura em regras de negócio
- [ ] Integrar relatórios de cobertura no CI

---

## Fase 9: CI/CD e Deploy

Objetivo: Automatizar o pipeline de entrega e preparar para produção.

### Etapa 9.1: Pipeline CI/CD (GitHub Actions)

```yaml
Stages:
  1. lint      → Ruff + ESLint
  2. test      → pytest + Jest
  3. build     → Docker build + push
  4. deploy    → Staging → Produção (aprovação manual)
```

- [ ] Configurar GitHub Actions
- [ ] Build e push de imagens Docker
- [ ] Deploy automático para staging
- [ ] Gate de aprovação para produção

### Etapa 9.2: Infraestrutura de Produção

- [ ] Kubernetes (EKS/GKE) ou AWS ECS
- [ ] Auto-scaling baseado em métricas
- [ ] PgBouncer para alta concorrência
- [ ] Read Replicas para queries pesadas

### Etapa 9.3: CDN e DNS (Brasil)

- [ ] Cloudflare ou AWS CloudFront com PoP em São Paulo
- [ ] DNS via Cloudflare (proteção DDoS)
- [ ] Certificados SSL/TLS

---

## Fase 10: Monitoramento e Observabilidade

Objetivo: Implementar stack completa de observabilidade para produção.

### Etapa 10.1: APM e Error Tracking

- [ ] Integrar Sentry (backend + mobile)
- [ ] Configurar alertas de crash
- [ ] Source maps para debugging

### Etapa 10.2: Métricas e Logs

- [ ] Prometheus + Grafana ou Datadog/New Relic
- [ ] Logs estruturados em JSON com `structlog`
- [ ] Centralização no CloudWatch ou ELK Stack

### Etapa 10.3: Alertas

- [ ] Latência > 500ms
- [ ] Error rate > 1%
- [ ] CPU/Memória acima de threshold
- [ ] Alertas de negócio (pagamentos falhos, etc.)

---

## Cronograma Estimado

| Fase | Duração Estimada | Dependências |
|------|------------------|--------------|
| Fase 1: Fundação | 2 semanas | - |
| Fase 2: Autenticação | 2 semanas | Fase 1 |
| Fase 3: Perfis e Geo | 3 semanas | Fase 2 |
| Fase 4: Agendamento | 3-4 semanas | Fase 3 |
| Fase 5: Pagamentos | 3-4 semanas | Fase 4 |
| Fase 6: Notificações | 2 semanas | Fase 4 |
| Fase 7: Avançado | 2-3 semanas | Fase 5, 6 |
| Fase 8: Testes | Paralelo às fases | - |
| Fase 9: CI/CD | 1-2 semanas | Fase 1, 8 |
| Fase 10: Monitoramento | 1 semana | Fase 9 |

**Total estimado: 16-20 semanas** (considerando paralelismo)

---

## Checklist de Compliance

- [ ] **LGPD**
  - [ ] Endpoints de exportação de dados
  - [ ] Endpoints de exclusão de dados
  - [ ] Consentimento explícito no cadastro
  - [ ] Política de privacidade

- [ ] **Segurança**
  - [ ] Senhas com hash bcrypt/argon2
  - [ ] Tokens nunca logados
  - [ ] Dados de pagamento nunca armazenados
  - [ ] HTTPS obrigatório

- [ ] **Financeiro**
  - [ ] Split atômico no Mercado Pago
  - [ ] Rastreabilidade de transações
  - [ ] Relatórios de conformidade

---

> **Nota:** Este plano deve ser revisado e atualizado conforme o projeto evolui. Alterações significativas devem ser refletidas no `PROJECT_GUIDELINES.md`.
