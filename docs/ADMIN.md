# Painel Administrativo GoDrive — Brainstorming & Melhores Práticas

> **Objetivo:** Organizar ideias, ferramentas e abordagens para construir um ecossistema administrativo completo que garanta total controle sobre o aplicativo GoDrive. Este documento **não é um plano de implementação**, mas sim uma referência estratégica para decisões futuras.

---

## Índice

1. [Estado Atual](#1-estado-atual)
2. [Suporte ao Usuário](#2-suporte-ao-usuário)
3. [Mediação de Disputas](#3-mediação-de-disputas)
4. [Monitoramento do Chat](#4-monitoramento-do-chat)
5. [Visualização Abrangente de Usuários](#5-visualização-abrangente-de-usuários)
6. [Monitoramento Completo do Sistema](#6-monitoramento-completo-do-sistema)
7. [Arquitetura do Painel Admin](#7-arquitetura-do-painel-admin)
8. [Comparativo de Abordagens](#8-comparativo-de-abordagens)
9. [Priorização Recomendada](#9-priorização-recomendada)

---

## 1. Estado Atual

O GoDrive já possui uma base administrativa usando **SQLAdmin**, integrado ao FastAPI:

| Recurso | Status | Observação |
|---------|--------|------------|
| Listagem de Usuários | ✅ Existe | Via `UserAdmin` (email, nome, tipo, ativo, verificado) |
| Perfis de Instrutores | ✅ Existe | Veículo, categoria, valor/hora, rating, disponibilidade |
| Perfis de Alunos | ✅ Existe | Estágio de aprendizado, categoria, total de aulas |
| Agendamentos | ✅ Existe | Data, status, aluno, instrutor, preço |
| Autenticação Admin | ✅ Existe | Via `AdminAuth` com JWT |
| Sistema de Disputas | ❌ Não existe | Fluxo planejado em `DISPUTE_FLOW.md`, sem backend |
| Monitoramento de Chat | ❌ Não existe | Chat funciona via WebSocket + Redis PubSub |
| Dashboard de Métricas | ❌ Não existe | Sem overview do sistema |
| Sistema de Suporte | ❌ Não existe | Sem tickets ou canal de atendimento |

### Limitações do SQLAdmin Atual

O SQLAdmin é excelente para CRUD rápido de tabelas, mas tem limitações para funcionalidades avançadas:
- **Sem dashboards customizados** (gráficos, KPIs, métricas em tempo real)
- **Sem lógica de workflow** (aprovar/rejeitar disputas com ações encadeadas)
- **Sem visualização de WebSocket** (chat em tempo real)
- **Sem permissões granulares** por funcionalidade (RBAC avançado)

> **Decisão-chave:** O SQLAdmin pode coexistir com soluções mais avançadas. Ele serve como ferramenta de acesso direto ao banco para operações simples, enquanto ferramentas especializadas cobrem as lacunas.

---

## 2. Suporte ao Usuário

### 2.1 Modelo de Suporte

Para um marketplace como o GoDrive, o suporte precisa ser **eficiente e escalonável**. As principais abordagens são:

#### Opção A: Help Center + Tickets In-App (Recomendado para MVP)

- **Como funciona:** O usuário abre um ticket dentro do app, classificando o problema. O suporte visualiza, responde e resolve via painel web.
- **Vantagens:** Controle total, sem dependência externa, os dados ficam no seu banco.
- **Ferramentas:**
  - **Construir internamente** — Tabela `support_tickets` + painel no admin + chat entre admin e usuário.
  - **Crisp** (plano gratuito para 2 agentes) — Widget de chat leve, SDK para React Native, sem overhead.
  - **Intercom** — Mais robusto, mas caro. Ideal se escalar rápido.

#### Opção B: FAQ + Chatbot Inteligente (Reduz Carga)

- **Como funciona:** Antes de abrir ticket, o usuário passa por um fluxo de autoatendimento com respostas automáticas para problemas comuns.
- **Vantagens:** Reduz volume de tickets em até 40-60%.
- **Implementação:**
  - Tela de FAQ dentro do app com categorias (Pagamento, Agendamento, Conta).
  - Chatbot simples com respostas pré-definidas baseadas em palavras-chave.
  - Se não resolver → escala para ticket com humano.

#### Opção C: Suporte via WhatsApp Business API

- **Como funciona:** O usuário é redirecionado para um número de WhatsApp do suporte.
- **Vantagens:** Familiar para o público brasileiro, baixa barreira de acesso.
- **Desvantagens:** Menos controle, difícil de rastrear métricas, não escala.

### 2.2 Recomendação para o GoDrive

```
Fase 1 (MVP):
  ├── FAQ in-app com respostas estáticas (zero custo)
  ├── Formulário "Fale Conosco" → cria ticket interno
  └── Painel Admin para gerenciar tickets

Fase 2 (Escala):
  ├── Chat in-app com agente (Crisp ou interno)
  ├── Classificação automática por tipo de problema
  └── SLA com alertas (tickets > 24h sem resposta)

Fase 3 (Automação):
  ├── Chatbot com árvore de decisão
  ├── Integração com base de conhecimento
  └── Métricas: tempo médio de resposta, satisfação (CSAT)
```

### 2.3 Modelo de Dados Sugerido (Tickets)

```
support_tickets
├── id (UUID)
├── user_id (FK → users)
├── category (enum: PAYMENT, SCHEDULING, ACCOUNT, DISPUTE, OTHER)
├── subject (varchar)
├── description (text)
├── status (enum: OPEN, IN_PROGRESS, WAITING_USER, RESOLVED, CLOSED)
├── priority (enum: LOW, MEDIUM, HIGH, URGENT)
├── assigned_to (UUID, nullable → admin user)
├── related_scheduling_id (UUID, nullable)
├── created_at, updated_at, resolved_at
└── satisfaction_rating (int 1-5, nullable → preenchido pelo user após resolução)
```

### 2.4 KPIs de Suporte a Monitorar

| Métrica | Alvo |
|---------|------|
| Tempo de primeira resposta | < 2 horas |
| Tempo de resolução | < 24 horas |
| Taxa de resolução no primeiro contato | > 70% |
| CSAT (satisfação) | > 4.0/5.0 |
| Tickets reabertos | < 5% |

---

## 3. Mediação de Disputas

### 3.1 Estado Atual do Fluxo

Conforme documentado em [`DISPUTE_FLOW.md`](file:///home/carloshf/udrive/docs/payments/DISPUTE_FLOW.md), o fluxo de disputas já tem uma base conceitual sólida:

- **Abertura:** Aluno relata problema após término da aula (motivos pré-definidos).
- **Transições:** `DISPUTED → COMPLETED | CANCELLED | CONFIRMED` (reagendamento).
- **Bloqueio:** O auto-complete ignora agendamentos em disputa.

### 3.2 O que Falta para o Painel de Disputas

#### A. Fila de Disputas (Inbox do Suporte)

O suporte precisa de uma **fila priorizada** de disputas abertas:

```
Fila de Disputas
├── Filtros: status, data, motivo, valor envolvido
├── Ordenação: mais antigas primeiro (FIFO) ou por valor (maior primeiro)
├── Badges: tempo desde abertura (🟢 < 6h, 🟡 6-24h, 🔴 > 24h)
└── Ação rápida: clicar → abre painel de detalhes da disputa
```

#### B. Painel de Detalhes da Disputa

Quando o admin abre uma disputa, precisa ver **tudo em uma tela**:

| Seção | Conteúdo |
|-------|----------|
| **Resumo** | Motivo relatado, data/hora da aula, valor, quem abriu |
| **Participantes** | Perfil do aluno (histórico de disputas, rating) + Perfil do instrutor (rating, total de aulas, reclamações anteriores) |
| **Histórico do Chat** | Todo o chat entre aluno e instrutor referente àquela aula (read-only para o admin) |
| **Telemetria** | Se disponível: localização GPS do início da aula, confirmação de presença |
| **Timeline** | Log cronológico de eventos: criação, pagamento, confirmação, abertura da disputa |
| **Notas Internas** | Campo para o admin escrever observações (não visíveis ao usuário) |
| **Ações** | Botões: Resolver a favor do Instrutor / Resolver a favor do Aluno / Mediar Reagendamento |

#### C. Tabela `disputes` (Auditoria)

Essencial para rastreabilidade e conformidade legal:

```
disputes
├── id (UUID)
├── scheduling_id (FK → schedulings)
├── opened_by (FK → users) — quem abriu
├── reason (enum: NO_SHOW, VEHICLE_ISSUE, LOCATION_NOT_FOUND, OTHER)
├── description (text) — relato livre do aluno
├── status (enum: OPEN, UNDER_REVIEW, RESOLVED_INSTRUCTOR, RESOLVED_STUDENT, RESOLVED_RESCHEDULE)
├── resolution_notes (text) — justificativa do admin
├── resolved_by (FK → admin users)
├── refund_amount (decimal, nullable)
├── refund_id (varchar, nullable → ID do reembolso no Mercado Pago)
├── created_at, updated_at, resolved_at
└── internal_notes (text[]) — notas internas do suporte
```

#### D. Ações Automatizadas

- **Notificação automática** ao abrir disputa → admin recebe alerta.
- **Escalação automática** → se disputa não é tratada em 24h, prioridade sobe para `URGENT`.
- **Notificação de resolução** → aluno e instrutor recebem push com o resultado.
- **Integração com reembolso** → ao resolver a favor do aluno, disparar reembolso via `RefundUseCase` (já existe o fluxo em [`MP_REFUNDS.md`](file:///home/carloshf/udrive/docs/payments/MP_REFUNDS.md)).

### 3.3 Métricas de Disputas

| Métrica | Por quê |
|---------|---------|
| Taxa de disputas / total de aulas | Saúde geral da plataforma (alvo: < 5%) |
| Tempo médio de resolução | Eficiência do suporte |
| Distribuição por motivo | Identifica problemas sistêmicos (ex: muitos "no-show" = problema de UX?) |
| Taxa de resolução por lado | Balança entre aluno vs instrutor (muito desequilibrado indica viés) |
| Instrutor reincidente | Instrutores com > 3 disputas merecem investigação |
| Valor total disputado vs. reembolsado | Impacto financeiro |

---

## 4. Monitoramento do Chat

### 4.1 Por que Monitorar?

- **Segurança:** Detectar assédio, linguagem abusiva, tentativas de negociação fora da plataforma ("me paga via Pix").
- **Qualidade:** Verificar se instrutores respondem em tempo hábil.
- **Disputas:** O histórico do chat é evidência primária na mediação.
- **Compliance:** Em caso de questões legais, ter logs acessíveis é fundamental.

### 4.2 Abordagens de Monitoramento

#### Nível 1: Acesso Read-Only sob Demanda (Recomendado Inicialmente)

- **Como:** O admin acessa o histórico de chat de uma conversa específica apenas quando necessário (ex: durante análise de disputa).
- **Implementação:** Endpoint admin que busca mensagens por `scheduling_id` ou `room_id`.
- **Vantagens:** Respeita privacidade, sem overhead, simples.
- **Boas práticas:** Registrar em log de auditoria toda vez que um admin acessar um chat.

#### Nível 2: Detecção Automática de Conteúdo Sensível

- **Como:** Filtro de palavras-chave aplicado no momento do envio da mensagem.
- **Implementação:** Middleware no `handle_send_message` que verifica contra lista de palavras/padrões.
- **Detectar:**
  - Linguagem abusiva (lista de termos)
  - Tentativas de bypass: "me paga direto", "pix", "meu número é", números de telefone
  - Links externos suspeitos
- **Ação:** Não bloquear a mensagem, mas criar um **flag/alerta** para o admin revisar.
- **Ferramentas:**
  - **Perspectiva API (Google)** — Gratuita, detecta toxicidade em texto. Suporta português.
  - **Regex patterns** para números de telefone e palavras-chave financeiras.
  - **Filtro interno simples** com operador `ILIKE` no PostgreSQL para buscas retroativas.

#### Nível 3: Moderação por IA (Futuro)

- **Como:** Modelo de ML classifica mensagens em tempo real (spam, abusivo, solicitação de contato externo).
- **Ferramentas:** OpenAI Moderation API (gratuita), Hugging Face models self-hosted.
- **Quando:** Quando o volume de chats justificar o investimento.

### 4.3 Dashboard de Chat para o Admin

```
Visão Geral do Chat
├── Total de conversas ativas (últimas 24h/7d/30d)
├── Mensagens enviadas por período
├── Tempo médio de resposta dos instrutores
├── Alertas pendentes (mensagens flagadas)
└── Conversas com mais mensagens (possíveis problemas)

Detalhes de uma Conversa
├── Participantes (com links para perfis)
├── Histórico completo (read-only, timeline)
├── Status da aula vinculada
├── Botão: "Abrir ticket de suporte"
└── Botão: "Desativar chat" (em casos extremos)
```

### 4.4 Modelo de Dados Sugerido (Flags)

```
chat_flags
├── id (UUID)
├── message_id (FK → messages)
├── room_id (FK → chat_rooms)
├── flag_type (enum: ABUSIVE_LANGUAGE, EXTERNAL_CONTACT, PHONE_NUMBER, SUSPICIOUS_LINK, OTHER)
├── flag_source (enum: AUTOMATIC, MANUAL_REPORT)
├── severity (enum: LOW, MEDIUM, HIGH)
├── status (enum: PENDING, REVIEWED, DISMISSED)
├── reviewed_by (UUID, nullable → admin user)
├── reviewed_at (timestamp, nullable)
└── created_at
```

---

## 5. Visualização Abrangente de Usuários

### 5.1 Perfil 360° do Usuário

O admin precisa ver **tudo sobre um usuário em uma página**. Isso é crítico para decisões de suporte e para entender padrões.

#### Para TODOS os Usuários:

```
Informações Gerais
├── Dados cadastrais (nome, email, telefone, foto, data de cadastro)
├── Status da conta (ativo, verificado, bloqueado)
├── Tipo de usuário (aluno/instrutor)
├── Última atividade (último login, última interação)
├── Dispositivo(s) registrado(s) (push tokens)
└── Geolocalização aproximada (cidade/estado)

Histórico de Atividade
├── Timeline de eventos: cadastro, aulas, pagamentos, disputas, tickets
├── Filtro por tipo de evento e período
└── Padrões: horários de uso, frequência de acesso

Segurança
├── Tentativas de login falhas
├── Histórico de redefinição de senha
├── IPs utilizados
└── Ações administrativas (bloqueio, advertência)
```

#### Para ALUNOS (visão adicional):

```
Dados Acadêmicos
├── Estágio de aprendizado, categoria almejada
├── Total de aulas realizadas / canceladas / disputadas
├── Instrutores utilizados (lista com rating dado)
├── Gasto total na plataforma
├── Frequência de uso (aulas/mês)
└── Taxa de cancelamento pessoal

Financeiro
├── Histórico de pagamentos (valor, data, status, meio)
├── Reembolsos recebidos
└── Método de pagamento preferido
```

#### Para INSTRUTORES (visão adicional):

```
Dados Profissionais
├── Valor da hora-aula (base), documento, categoria
├── Rating médio, total de avaliações
├── Total de aulas realizadas / canceladas / disputadas
├── Alunos atendidos (lista)
├── Taxa de ocupação (horários preenchidos vs. disponíveis)
└── Zona de atuação (mapa de calor)

Financeiro
├── Earnings totais, mensais, pendentes
├── Histórico de repasses (Mercado Pago splits)
├── Taxas retidas
└── Conta Mercado Pago vinculada (status do vínculo)

Compliance
├── Documentação verificada? (CNH, CRLV)
├── Disputas recebidas vs. resolvidas a favor
├── Reclamações de alunos
└── Score de confiabilidade (calculado)
```

### 5.2 Ações Administrativas sobre Usuários

| Ação | Descrição | Log? |
|------|-----------|------|
| Desativar conta | `is_active = false`, impede login | ✅ |
| Suspender temporariamente | Bloqueia por período definido | ✅ |
| Enviar advertência | Notificação formal in-app | ✅ |
| Forçar logout | Invalida todos os refresh tokens | ✅ |
| Resetar senha | Envia link de redefinição | ✅ |
| Verificar manualmente | Marca documentação como verificada | ✅ |
| Exportar dados (LGPD) | Gera JSON/CSV com todos os dados do user | ✅ |
| Excluir conta (LGPD) | Anonimiza dados pessoais, mantém financeiro para auditoria | ✅ |

### 5.3 Busca e Filtros Avançados

```
Busca Global
├── Por nome, email, telefone, ID
├── Filtros combinados:
│   ├── Tipo: aluno / instrutor / todos
│   ├── Status: ativo / inativo / bloqueado
│   ├── Período de cadastro
│   ├── Última atividade (inativo > 30/60/90 dias)
│   ├── Com disputas abertas
│   ├── Rating abaixo de X
│   └── Região (cidade/estado)
└── Exportar resultado em CSV/JSON
```

---

## 6. Monitoramento Completo do Sistema

### 6.1 Camadas de Monitoramento

O monitoramento profissional opera em **4 camadas**:

```
┌─────────────────────────────────────────┐
│  Camada 4: NEGÓCIO (Business Metrics)   │  ← KPIs do marketplace
├─────────────────────────────────────────┤
│  Camada 3: APLICAÇÃO (APM)              │  ← Erros, latência, traces
├─────────────────────────────────────────┤
│  Camada 2: INFRAESTRUTURA               │  ← CPU, RAM, disco, rede
├─────────────────────────────────────────┤
│  Camada 1: LOGS (Observabilidade)       │  ← Logs estruturados
└─────────────────────────────────────────┘
```

### 6.2 Camada 1: Logs Estruturados

O `PROJECT_GUIDELINES.md` já define o uso de **structlog** com output JSON.

#### Ferramenta Recomendada: Stack de Logging

| Opção | Custo | Melhor para |
|-------|-------|-------------|
| **Grafana Loki + Promtail** | Gratuito (self-hosted) | TimeTeam pequeno, já usa Docker |
| **ELK Stack (Elasticsearch + Logstash + Kibana)** | Gratuito (self-hosted), pesado | Busca full-text em logs, alto volume |
| **AWS CloudWatch Logs** | Pay-per-use | Se já estiver na AWS |
| **Better Stack (Logtail)** | Free tier generoso | SaaS zero-config, fácil de começar |
| **Datadog Logs** | Caro | Enterprise, tudo-em-um |

**Recomendação:** **Grafana Loki** se self-hosted (já vai usar Grafana para dashboards), ou **Better Stack** para começar rápido com SaaS.

#### Boas Práticas de Logging para o GoDrive:

```python
# Estrutura ideal de log (já usando structlog)
logger.info(
    "scheduling_created",
    scheduling_id=str(scheduling.id),
    student_id=str(student.id),
    instructor_id=str(instructor.id),
    price=float(scheduling.price),
    scheduled_for=scheduling.scheduled_datetime.isoformat(),
    duration_ms=elapsed,
)
```

- **Sempre** incluir IDs de entidades (`scheduling_id`, `user_id`, etc.) — permite rastrear por transação.
- **Nunca** logar dados sensíveis (tokens, senhas, dados de cartão).
- **Categorizar** eventos: `scheduling_*`, `payment_*`, `chat_*`, `auth_*`, `dispute_*`.
- **Medir duração** de operações críticas (pagamento, busca geo, etc.).

### 6.3 Camada 2: Infraestrutura

#### O que Monitorar:

| Componente | Métricas | Alerta quando |
|-----------|----------|-------------|
| **Backend (FastAPI)** | CPU, RAM, conexões ativas, request count | CPU > 80%, RAM > 85% |
| **PostgreSQL** | Conexões ativas, query time, pool usage, disco | Conexões > 80% do pool, query > 1s |
| **Redis** | Memória usada, keys expiradas, hit rate | Memória > 70%, hit rate < 80% |
| **Celery Workers** | Tasks na fila, tempo de execução, falhas | Fila > 100, falha rate > 5% |
| **Docker Containers** | Status, restart count, resource usage | Restart > 3 em 5min |

#### Ferramentas:

| Opção | Custo | Stack |
|-------|-------|-------|
| **Prometheus + Grafana** | Gratuito (self-hosted) | Padrão da indústria para métricas + dashboards |
| **Datadog** | ~$15/host/mês | SaaS all-in-one, fácil setup |
| **New Relic** | Free tier (100GB/mês) | SaaS, ótimo para começar |
| **Netdata** | Gratuito (self-hosted) | Zero-config, dashboards incríveis out-of-the-box |

**Recomendação:** **Prometheus + Grafana** (indústria padrão, gratuito, infinitamente customizável). Adicionar **exporters** para PostgreSQL e Redis.

Integração com FastAPI:
```python
# Biblioteca: prometheus-fastapi-instrumentator
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### 6.4 Camada 3: Application Performance Monitoring (APM)

#### O que Monitorar:

- **Erros em tempo real** com stack trace completo.
- **Performance de endpoints** (latência p50, p95, p99).
- **Traces distribuídos** (request → DB → Redis → Mercado Pago).
- **Crash reports do mobile** (Expo/React Native).

#### Ferramentas:

| Opção | Custo | Melhor para |
|-------|-------|-------------|
| **Sentry** | Free tier (5K events/mês) | Erros + Performance, SDK para Python e React Native |
| **Datadog APM** | $31/host/mês | Traces distribuídos, correlação com logs |
| **New Relic** | Free tier | Full-stack observability |
| **OpenTelemetry + Jaeger** | Gratuito (self-hosted) | Traces distribuídos open-source |

**Recomendação:** **Sentry** — já mencionado no `PROJECT_GUIDELINES.md`. SDK nativo para FastAPI e Expo. O free tier é suficiente para MVP.

```python
# Backend
import sentry_sdk
sentry_sdk.init(dsn="...", traces_sample_rate=0.2)

# Mobile
import * as Sentry from '@sentry/react-native';
Sentry.init({ dsn: '...' });
```

### 6.5 Camada 4: Métricas de Negócio (Dashboard Admin)

Este é o **diferencial** — um dashboard que mostra a saúde do marketplace em tempo real:

#### KPIs Essenciais:

```
Dashboard Principal
├── Visão Geral
│   ├── Usuários totais (alunos + instrutores)
│   ├── Novos cadastros (hoje / 7d / 30d)
│   ├── Usuários ativos (DAU / MAU)
│   └── Taxa de retenção (D7, D30)
│
├── Aulas
│   ├── Aulas agendadas (hoje / 7d / 30d)
│   ├── Aulas completadas vs. canceladas (%)
│   ├── Taxa de no-show
│   ├── Tempo médio entre cadastro e primeira aula (funil)
│   └── Horários de pico (heatmap por dia/hora)
│
├── Financeiro
│   ├── GMV (Gross Merchandise Value) — valor bruto transacionado
│   ├── Receita da plataforma (comissões)
│   ├── Ticket médio
│   ├── Reembolsos emitidos (volume + percentual)
│   └── Valores em disputa
│
├── Suporte
│   ├── Tickets abertos vs. resolvidos
│   ├── Tempo médio de resolução
│   ├── Disputas abertas
│   └── CSAT score
│
└── Saúde Técnica
    ├── Uptime (API + DB + Redis)
    ├── Latência média da API
    ├── Taxa de erros (4xx, 5xx)
    └── Celery: tasks pendentes / falhadas
```

#### Implementação do Dashboard:

**Opção A: Grafana Dashboards (Recomendado)**
- Conecta diretamente ao PostgreSQL para métricas de negócio.
- Conecta ao Prometheus para métricas de infra.
- Dashboards customizáveis com SQL queries.
- Alertas integrados (Slack, Email, PagerDuty).
- **Custo:** Gratuito (self-hosted) ou Grafana Cloud (free tier).

**Opção B: Metabase**
- Focado em BI/analytics, não em monitoramento técnico.
- Interface amigável para não-técnicos.
- Bom para relatórios financeiros e de negócio.
- **Custo:** Gratuito (self-hosted).

**Opção C: Dashboard Customizado no Admin**
- Construir dentro do próprio painel admin (React/Next.js).
- Total controle visual e funcional.
- Mais trabalho de desenvolvimento.
- Usar bibliotecas: **Recharts**, **Chart.js**, **Tremor** (React).

**Recomendação prática:**
- **Grafana** para monitoramento técnico (infra + application).
- **Dashboard customizado no admin** para métricas de negócio (user-facing para o time operacional).

### 6.6 Sistema de Alertas

Alertas devem ser **acionáveis** e **não ruidosos**:

| Tipo | Canal | Exemplos |
|------|-------|----------|
| **Crítico (P0)** | SMS + Push + Slack | API down, DB unreachable, erro 500 > 10% |
| **Alto (P1)** | Slack + Email | Latência > 2s, Celery queue > 500, disputa > 48h sem resposta |
| **Médio (P2)** | Slack (canal específico) | Novo cadastro de instrutor para verificar, taxa de cancelamento subiu |
| **Baixo (P3)** | Dashboard (visual) | Picos de uso, métricas de vaidade |

---

## 7. Arquitetura do Painel Admin

### 7.1 Abordagens Possíveis

#### Opção A: SQLAdmin Expandido (Mínimo Esforço)

```
Prós:
  ├── Já está funcionando
  ├── Zero frontend para manter
  └── ModelViews para novas tabelas (disputes, tickets, flags) são triviais

Contras:
  ├── Limitado: sem dashboards, sem workflow, sem chat viewer
  ├── UX não customizável
  └── Não escala para funcionalidades avançadas
```

**Veredicto:** Manter para CRUD básico, não tentar forçar funcionalidades complexas nele.

#### Opção B: Admin API + Frontend React/Next.js (Recomendado)

```
Prós:
  ├── Controle total da UX e funcionalidades
  ├── Dashboards customizados, workflow de disputas, chat viewer
  ├── Reutiliza o backend FastAPI (novos endpoints /api/v1/admin/*)
  ├── Pode usar bibliotecas como Tremor, shadcn/ui, Recharts
  └── Escala infinitamente

Contras:
  ├── Mais trabalho inicial de desenvolvimento
  └── Mais código para manter (frontend separado)
```

**Veredicto:** Melhor opção para médio/longo prazo. Começa pequeno, cresce conforme necessidade.

#### Opção C: Ferramentas Low-Code (Retool, Appsmith)

```
Prós:
  ├── Rapidez absurda: conecta ao banco e monta telas em horas
  ├── Componentes prontos: tabelas, gráficos, formulários, workflows
  ├── Conexão direta com PostgreSQL e APIs REST
  └── Ideal para times pequenos sem frontend dedicado para admin

Contras:
  ├── Vendor lock-in (dependência da plataforma)
  ├── Custo mensal (Retool: ~$10/user/mês, Appsmith: free tier generoso)
  ├── Limitações em customizações muito específicas
  └── Dados sensíveis passam pela plataforma
```

**Veredicto:** Excelente para validar rapidamente, mas considerar trade-offs de dependência e custo.

### 7.2 Arquitetura Recomendada (Híbrida)

```
┌─────────────────────────────────────────────────────┐
│                    Browser Admin                     │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ SQLAdmin │  │ Admin Panel  │  │   Grafana     │ │
│  │ (CRUD    │  │ (React/Next) │  │ (Métricas     │ │
│  │  rápido) │  │              │  │  + Alertas)   │ │
│  └────┬─────┘  └──────┬───────┘  └───────┬───────┘ │
│       │               │                  │          │
└───────┼───────────────┼──────────────────┼──────────┘
        │               │                  │
    ┌───▼───────────────▼──────┐    ┌──────▼──────┐
    │      FastAPI Backend     │    │ Prometheus  │
    │  /admin/* (SQLAdmin)     │    │ /metrics    │
    │  /api/v1/admin/*         │    └─────────────┘
    │     (endpoints admin)    │
    └──────────┬───────────────┘
               │
    ┌──────────▼──────────┐
    │  PostgreSQL + Redis  │
    └─────────────────────┘
```

### 7.3 RBAC (Role-Based Access Control) para Admin

```
Roles
├── SUPER_ADMIN — acesso total
├── SUPPORT_AGENT — tickets, disputas, chat (read), perfis de usuário
├── FINANCE_ADMIN — dashboard financeiro, reembolsos, pagamentos
├── MODERATOR — flags de chat, advertências, bloqueios
└── VIEWER — dashboards read-only (métricas, relatórios)
```

**Implementação:** Tabela `admin_users` separada da `users`, com campo `role`. Middleware de permissão nos endpoints `/api/v1/admin/*`.

---

## 8. Comparativo de Abordagens

### Stack de Monitoramento

| Componente | MVP (Baixo Custo) | Produção (Profissional) |
|------------|-------------------|------------------------|
| **Erros/Crashes** | Sentry (free tier) | Sentry (paid) |
| **Métricas Infra** | Netdata (zero-config) | Prometheus + Grafana |
| **Logs** | `structlog` → stdout + Docker logs | Grafana Loki ou Better Stack |
| **Métricas Negócio** | Queries SQL manuais | Grafana + Metabase |
| **Alertas** | Sentry alerts | Grafana Alerts → Slack/PagerDuty |
| **APM/Traces** | Sentry Performance | OpenTelemetry + Jaeger |

### Stack do Admin Panel

| Componente | MVP | Produção |
|------------|-----|----------|
| **CRUD de dados** | SQLAdmin (já existe) | SQLAdmin (manter) |
| **Disputas** | SQLAdmin + scripts | Admin Panel custom |
| **Suporte** | Google Forms + Planilha | Sistema de tickets in-app + painel |
| **Chat Monitor** | Query SQL direta | Painel com viewer + flags automáticos |
| **User Profile** | SQLAdmin views | Perfil 360° no painel custom |
| **Dashboard** | Nenhum | Grafana + Dashboard custom |

---

## 9. Priorização Recomendada

Baseado no impacto para a operação e complexidade de implementação:

### 🔴 Prioridade 1 — Fundação Operacional

| Item | Justificativa |
|------|--------------|
| **Sistema de Disputas (backend + admin)** | Sem isso, aulas problemáticas travam o fluxo financeiro |
| **Sentry (backend + mobile)** | Visibilidade de erros é o mínimo para produção |
| **Logs estruturados centralizados** | Debugging sem logs é impossível em produção |

### 🟡 Prioridade 2 — Controle Operacional

| Item | Justificativa |
|------|--------------|
| **Dashboard de métricas de negócio** | Sem dados, você opera no escuro |
| **Perfil 360° do usuário no admin** | Suporte eficiente depende de contexto completo |
| **Sistema de tickets básico** | Canal formal de comunicação com usuários |

### 🟢 Prioridade 3 — Escala e Automação

| Item | Justificativa |
|------|--------------|
| **Monitoramento de chat (flags)** | Importante mas pode começar manual |
| **Alertas automatizados (Grafana)** | Proativo em vez de reativo |
| **Prometheus + Grafana (infra)** | Essencial para produção com escala |
| **RBAC para admin** | Necessário quando houver mais de 1 pessoa no suporte |

### 🔵 Prioridade 4 — Diferenciação

| Item | Justificativa |
|------|--------------|
| **Chatbot de autoatendimento** | Reduz carga do suporte |
| **Moderação por IA no chat** | Volume precisa justificar |
| **Relatórios automatizados** | Exportações e reports periódicos |
| **Heat maps e analytics avançados** | Dados de uso para decisões de produto |

---

## Referências

- [`PROJECT_GUIDELINES.md`](file:///home/carloshf/udrive/docs/architeture/PROJECT_GUIDELINES.md) — Stack e padrões do projeto
- [`DISPUTE_FLOW.md`](file:///home/carloshf/udrive/docs/payments/DISPUTE_FLOW.md) — Fluxo de disputas planejado
- [`PAYMENT_FLOW.md`](file:///home/carloshf/udrive/docs/payments/PAYMENT_FLOW.md) — Fluxo de pagamento e precificação
- [`NOTIFICATIONS.md`](file:///home/carloshf/udrive/docs/architeture/NOTIFICATIONS.md) — Sistema de notificações tri-canal
- [`MP_REFUNDS.md`](file:///home/carloshf/udrive/docs/payments/MP_REFUNDS.md) — Fluxo de reembolsos via Mercado Pago
- [SQLAdmin existente](file:///home/carloshf/udrive/backend/src/interface/admin/views.py) — Views atuais do painel
