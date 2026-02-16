# PROJECT GUIDELINES: GoDrive (UDrive)

Este arquivo é a **Fonte Única da Verdade** para o desenvolvimento deste projeto. Agentes de IA e desenvolvedores devem seguir estas regras estritamente.

## 1. Visão do Produto
O **GoDrive** é um Marketplace SaaS para conectar alunos a instrutores de direção independentes.
- **Core Value:** Agilidade para alunos, gestão financeira para instrutores.
- **Crítico:** Geolocalização precisa, pagamentos seguros (split) e alta disponibilidade.

---

## 2. Stack Tecnológica (Versões Definidas)

### Mobile (Frontend)
- **Framework:** React Native (Expo Managed Workflow).
- **Linguagem:** TypeScript (Strict Mode obrigatório).
- **Estado Global:** Zustand (Client State).
- **Estado do Servidor:** TanStack Query (React Query) v5+ (Obrigatório para cache e requisições).
- **Mapas:** `react-native-maps`.
- **HTTP:** Axios (configurado dentro do QueryFn do React Query).
- **Estilização:** NativeWind (TailwindCSS para React Native) para consistência e produtividade.

### Backend (API)
- **Linguagem:** Python 3.10+.
- **Framework:** FastAPI (Assíncrono).
- **Banco de Dados:** PostgreSQL 15+ com extensão **PostGIS** (Geometria é vital).
- **ORM:** SQLAlchemy 2.0+ (Sintaxe moderna `select()`, não usar `Query` legado).
- **Validação:** Pydantic v2.
- **Cache/PubSub:** Redis (para busca de instrutores e WebSockets).
- **Task Queue:** Celery + Redis (para tarefas assíncronas pesadas).

### Autenticação
- **Padrão:** JWT (OAuth2) com `python-jose` ou `authlib`.
- **Refresh Tokens:** Com rotação obrigatória.
- **Armazenamento Mobile:** `expo-secure-store` (nunca usar AsyncStorage para tokens).
- **Expiração:** Access Token = 15min, Refresh Token = 7 dias.

---

## 3. Arquitetura e Estrutura de Pastas

### Backend: Clean Architecture (Modular)
O código deve ser desacoplado. A lógica de negócio **NÃO** deve depender do FastAPI ou SQLAlchemy diretamente.

```text
backend/src/
├── domain/            # Entidades puras e Interfaces (Protocolos)
│   ├── entities/      # Ex: Agendamento, Instrutor (Dataclasses/Pydantic puros)
│   └── interfaces/    # Ex: IAgendamentoRepository (Abstração)
├── application/       # Casos de Uso (Regras de Negócio)
│   └── use_cases/     # Ex: criar_agendamento.py, calcular_split.py
├── infrastructure/    # Implementações externas
│   ├── db/            # SQLAlchemy Models, Alembic
│   ├── repositories/  # Implementação concreta de IAgendamentoRepository
│   └── external/      # Integrações (Stripe, Maps API)
└── interface/         # Pontos de entrada
    ├── api/           # Routers FastAPI, Controllers
    └── websockets/    # Gerenciadores de conexão Socket
```

### Mobile: Feature-Based Architecture

Organize o código por funcionalidade, não por tipo técnico.

```plaintext
mobile/src/
├── app/               # Expo Router (se aplicável) ou Navegação
├── features/          # Módulos isolados
│   ├── auth/          # Login, Cadastro, Recuperação
│   ├── map/           # Visualização de instrutores, Rastreamento
│   └── scheduling/    # Agendamento, Pagamento
│       ├── components/# Componentes exclusivos desta feature
│       ├── hooks/     # Custom hooks (logica de UI)
│       └── api/       # Funções de fetch específicas
├── shared/            # Componentes reutilizáveis globais (Botões, Inputs)
└── lib/               # Configurações (Axios, QueryClient, Zustand Store)
```

### 3.1 Mobile: Separação por Tipo de Usuário

O GoDrive possui dois tipos de usuários com interfaces **completamente distintas**. A estrutura deve refletir isso explicitamente:

```plaintext
mobile/src/
├── features/
│   ├── student-app/               # Tudo exclusivo do ALUNO
│   │   ├── screens/               # Telas do aluno
│   │   ├── components/            # Componentes específicos
│   │   ├── navigation/            # StudentTabNavigator
│   │   └── hooks/                 # Hooks específicos
│   ├── instructor-app/            # Tudo exclusivo do INSTRUTOR
│   │   ├── screens/               # Telas do instrutor
│   │   ├── components/            # Componentes específicos
│   │   ├── navigation/            # InstructorTabNavigator
│   │   └── hooks/                 # Hooks específicos
│   ├── auth/                      # Compartilhado (login, cadastro)
│   └── shared-features/           # Features usadas por AMBOS
│       ├── scheduling/            # Lógica de agendamento compartilhada
│       ├── chat/                  # Mensagens entre aluno e instrutor
│       └── payments/              # Telas de pagamento/recebimento
├── shared/                        # UI components agnósticos
│   ├── components/
│   ├── hooks/
│   └── lib/
└── navigation/
    └── RootNavigator.tsx          # Decide qual stack baseado no user_type
```

**Regras:**
- **Nunca** espalhar `if (userType === 'instructor')` pelo código
- Features exclusivas de cada tipo devem evoluir independentemente
- Componentes visuais reutilizáveis ficam em `shared/components/`

### 3.2 Backend: Use Cases por Domínio de Usuário

Organizar casos de uso por tipo de usuário para manter regras de negócio isoladas:

```plaintext
backend/src/application/use_cases/
├── common/                        # Use cases compartilhados
│   ├── update_profile.py
│   └── get_notifications.py
├── student/                       # Use cases exclusivos do ALUNO
│   ├── search_instructors.py
│   ├── book_lesson.py
│   ├── cancel_booking.py
│   └── rate_instructor.py
└── instructor/                    # Use cases exclusivos do INSTRUTOR
    ├── set_availability.py
    ├── manage_schedule.py
    ├── accept_booking.py
    └── view_earnings.py
```

### 3.3 Backend: API Routes por Prefixo de Usuário

Endpoints devem ser agrupados por tipo de usuário na camada de interface:

```plaintext
backend/src/interface/api/
├── v1/
│   ├── auth/                      # /api/v1/auth/* (público)
│   ├── student/                   # /api/v1/student/* (endpoints do aluno)
│   │   ├── instructors.py         # Busca de instrutores
│   │   ├── lessons.py             # Agendamentos do aluno
│   │   └── payments.py            # Pagamentos realizados
│   ├── instructor/                # /api/v1/instructor/* (endpoints do instrutor)
│   │   ├── availability.py        # Gestão de horários
│   │   ├── schedule.py            # Agenda e confirmações
│   │   └── earnings.py            # Dashboard financeiro
│   └── shared/                    # Endpoints que ambos usam
│       ├── profile.py
│       └── notifications.py
```

### 3.4 Navegação por Tipo de Usuário

```typescript
// mobile/src/navigation/RootNavigator.tsx
const RootNavigator = () => {
  const { user } = useAuth();

  if (!user) return <AuthStack />;

  // Navegação condicional baseada no tipo de usuário
  return user.userType === 'instructor' 
    ? <InstructorTabNavigator /> 
    : <StudentTabNavigator />;
};
```

**Tab Navigators:**

| StudentTabNavigator | InstructorTabNavigator |
|---------------------|------------------------|
| Home                | Dashboard              |
| Buscar Instrutores  | Agenda                 |
| Meus Agendamentos   | Meus Alunos            |
| Perfil              | Perfil                 |

### 3.5 Guards de Permissão (Backend)

Criar dependencies para validar o tipo de usuário nos endpoints:

```python
# backend/src/interface/api/dependencies.py
from fastapi import Depends, HTTPException, status

def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Garante que apenas alunos acessem este endpoint."""
    if current_user.user_type != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para alunos"
        )
    return current_user

def require_instructor(current_user: User = Depends(get_current_user)) -> User:
    """Garante que apenas instrutores acessem este endpoint."""
    if current_user.user_type != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para instrutores"
        )
    return current_user
```

**Uso nos routers:**
```python
@router.get("/earnings")
async def get_earnings(
    instructor: User = Depends(require_instructor)
):
    # Apenas instrutores chegam aqui
    ...
```

---

## 4. Regras de Codificação (Coding Standards)

### Geral

- **Idioma:** Código (variáveis, funções) em **Inglês**. Comentários e Commits em **Português**.
- **SOLID:** Princípio da Responsabilidade Única (SRP) e Inversão de Dependência (DIP) são inegociáveis.

### Python (Backend)

- **Type Hints:** Obrigatório em 100% das assinaturas de função.
- **Docstrings:** Google Style Guide para módulos e funções públicas.
- **Tratamento de Erros:** Use exceções customizadas de domínio (ex: `DriverNotFoundException`) e mapeie para HTTP Status Codes apenas na camada `interface/api`.
- **Testes:** `pytest`. Use `conftest.py` para fixtures. Mocks apenas para I/O externo.

### TypeScript (Mobile)

- **Interfaces:** Prefira `interface` a `type` para definições de objetos.
- **Componentes:** Funcionais. Use hooks para lógica. Nunca coloque lógica complexa dentro do JSX/TSX.
- **Performance:** Use `useCallback` e `useMemo` para funções passadas como props em listas grandes (Mapas/Listas de Instrutores).

---

## 5. Regras de Negócio Críticas (Hard Constraints)

1. **Cancelamento:**
    - `IF` tempo_para_aula > 24h `THEN` reembolso = 100%.
    - `IF` tempo_para_aula < 24h `THEN` multa = 50%.

2. **Geolocalização:**
    - Updates de posição: a cada **5s** (movimento) ou **30s** (parado).
    - Raio de busca padrão: Configurable (ex: 10km).

3. **Financeiro:**
    - O Split de pagamento deve ocorrer **atomicamente** na transação do Stripe. Não acumular saldo na plataforma para distribuir depois (risco fiscal).

---

## 6. Infraestrutura e Deploy

### Containerização
- **Docker + Docker Compose** para desenvolvimento local.
- **Kubernetes (EKS/GKE)** ou **AWS ECS** para produção (auto-scaling).

### CI/CD Pipeline
- **Ferramenta:** GitHub Actions ou GitLab CI.
- **Stages obrigatórios:**
  1. `lint` → Ruff (Python), ESLint (TypeScript)
  2. `test` → pytest (Backend), Jest (Mobile)
  3. `build` → Docker build + push to registry
  4. `deploy` → Staging → Produção (com aprovação manual)

### Monitoramento e Observabilidade
- **APM:** Sentry (erros e crash reports).
- **Métricas:** Datadog, New Relic ou Prometheus + Grafana.
- **Logs:** Estruturados em JSON com `structlog` (Python). Centralizados no CloudWatch ou ELK Stack.
- **Alertas:** Configurar para latência > 500ms, error rate > 1%, e uso de CPU/memória.

### CDN e Edge (Brasil)
- **CDN:** Cloudflare ou AWS CloudFront com PoP em São Paulo.
- **DNS:** Cloudflare (proteção DDoS inclusa).

---

## 7. Segurança

### Rate Limiting
- **Biblioteca:** `slowapi` no FastAPI.
- **Limites sugeridos:**
  - Login: 5 tentativas/minuto por IP.
  - API geral: 100 requests/minuto por usuário autenticado.
  - Endpoints públicos: 30 requests/minuto por IP.

### Headers e CORS
- **CORS:** Strict para domínios conhecidos (não usar `*` em produção).
- **Headers de Segurança:**
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Strict-Transport-Security` (HSTS)

### Proteção de Dados
- **Senhas:** Hash com `bcrypt` ou `argon2`.
- **Dados Sensíveis:** Nunca logar tokens, senhas ou dados de pagamento.
- **LGPD:** Implementar endpoints para exportação e exclusão de dados do usuário.

---

## 8. Database Scaling

### Connection Pooling
- **SQLAlchemy Async:** Usar `pool_size=20`, `max_overflow=10` como base.
- **PgBouncer:** Considerar para produção com alta concorrência (> 1000 conexões simultâneas).

### Read Replicas
- Para queries pesadas (dashboards, relatórios, histórico), direcionar para **Read Replica**.
- Manter escrita apenas no **Primary**.

### Índices Críticos
- **PostGIS:** Índice GIST para colunas de geometria.
- **Busca por usuário:** Índice em `user_id`, `created_at`.
- **Status:** Índice em campos de status frequentemente filtrados.

---

## 9. Migrations (Alembic)

### Regras
- **Uma migration por feature branch.**
- **Naming convention:** `{YYYY_MM_DD}_{descricao_snake_case}` (ex: `2024_01_15_criar_tabela_agendamentos`).
- **Nunca editar migrations já mergeadas na main.**
- **Sempre testar rollback:** `alembic downgrade -1` antes de merge.
- **Migrations manuais:** Não usar `--autogenerate` para evitar código verbose e desnecessário.

### Comandos Padrão
```bash
# Criar nova migration (manual - sem autogenerate)
alembic revision -m "descricao_da_mudanca"

# Aplicar migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Verificar status atual
alembic current

# Histórico de migrations
alembic history
```

### Template de Migration
O arquivo gerado terá funções `upgrade()` e `downgrade()` vazias. Preencha manualmente:

```python
"""descricao_da_mudanca

Revision ID: abc123
Revises: def456
Create Date: 2024-01-15 10:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "abc123"
down_revision: str | None = "def456"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica a migration."""
    op.create_table(
        "nome_tabela",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("campo", sa.String(255), nullable=False),
    )


def downgrade() -> None:
    """Reverte a migration."""
    op.drop_table("nome_tabela")
```

> **Dica:** Para referência de operações Alembic, consulte: `op.create_table`, `op.drop_table`, `op.add_column`, `op.drop_column`, `op.create_index`, `op.drop_index`.

---

## 10. Task Queue (Tarefas Assíncronas)

### Quando Usar
- Envio de notificações push/email em massa.
- Geração de relatórios financeiros.
- Processamento de imagens (foto de perfil).
- Sincronização com APIs externas (Stripe webhooks retry).

### Stack
- **Celery** + **Redis** (broker e backend).
- Alternativa async-native: `taskiq` ou `arq`.

### Estrutura
```text
backend/src/infrastructure/
└── tasks/
    ├── __init__.py
    ├── celery_app.py      # Configuração do Celery
    ├── notifications.py   # Tasks de notificação
    └── reports.py         # Tasks de relatórios
```

---

## 11. Fluxo de Trabalho do Agente

Ao receber uma tarefa:

1. **Analise:** Identifique quais camadas da Clean Architecture serão afetadas.
2. **Planeje:** Liste os arquivos a serem criados/editados antes de escrever código.
3. **Implemente:** Comece pelo **Domain** (Entidades), depois **Application** (Casos de Uso), e por fim **Infrastructure/Interface**.
4. **Verifique:** Garanta que não quebrou os princípios SOLID.
5. **Documente:** Atualize este arquivo se houver mudanças arquiteturais significativas.