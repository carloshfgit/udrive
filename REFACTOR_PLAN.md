# REFACTOR_PLAN.md - Reestruturação do GoDrive

Este documento detalha o plano completo para reestruturar o projeto GoDrive conforme as novas diretrizes do `PROJECT_GUIDELINES.md`, tornando-o mais profissional e escalável para lidar com dois tipos de usuários distintos (aluno e instrutor).

---

## Análise do Estado Atual

### Mobile (`mobile/src/`)

| Pasta | Status | Problema |
|-------|--------|----------|
| `features/instructor-app/` | ✅ Parcialmente alinhado | Já existe, mas pode precisar de mais conteúdo |
| `features/auth/` | ✅ OK | Feature compartilhada |
| `features/profile/` | ⚠️ Não segmentado | Código de aluno e instrutor misturados |
| `features/search/` | ⚠️ Exclusivo de aluno | Deveria estar em `student-app/` |
| `features/scheduling/` | ⚠️ Não segmentado | Usado por ambos mas com views diferentes |
| `features/home/` | ⚠️ Ambíguo | Deveria estar em `student-app/` |
| `features/map/` | ⚠️ Exclusivo de aluno | Deveria estar em `student-app/` |
| `features/learning/` | ⚠️ Exclusivo de aluno | Deveria estar em `student-app/` |
| `navigation/` | ✅ Bom | Já tem `RootNavigator`, `StudentTabNavigator`, `InstructorTabNavigator` |

### Backend (`backend/src/`)

| Camada | Status | Problema |
|--------|--------|----------|
| `application/use_cases/` | ⚠️ Flat | Arquivos soltos, sem organização por tipo de usuário |
| `interface/api/routers/` | ⚠️ Flat | Routers genéricos (`instructors.py`, `students.py`) sem prefixo de usuário |
| `interface/api/dependencies.py` | ⚠️ Incompleto | Faltam guards `require_student` e `require_instructor` |
| `domain/` | ✅ Bom | Entidades bem organizadas |
| `infrastructure/` | ✅ Bom | Repositórios bem estruturados |

---

## Plano de Refatoração

### Fase 1: Reorganização Mobile (Prioridade Alta)

#### Etapa 1.1: Criar estrutura `student-app/`

Criar a pasta `features/student-app/` e mover features exclusivas do aluno:

```bash
# Criar estrutura
mkdir -p mobile/src/features/student-app/{screens,components,hooks,api,navigation}

# Mover features exclusivas do aluno
mv mobile/src/features/search/* mobile/src/features/student-app/search/
mv mobile/src/features/map/* mobile/src/features/student-app/map/
mv mobile/src/features/home/* mobile/src/features/student-app/home/
mv mobile/src/features/learning/* mobile/src/features/student-app/learning/
```

**Estrutura resultante:**
```plaintext
mobile/src/features/
├── student-app/
│   ├── screens/               # HomeScreen, SearchScreen, etc.
│   ├── components/
│   ├── hooks/
│   ├── api/
│   └── navigation/
│       └── StudentTabNavigator.tsx
├── instructor-app/            # (já existe)
│   ├── screens/
│   ├── components/
│   ├── hooks/
│   ├── api/
│   └── navigation/
│       └── InstructorTabNavigator.tsx
├── auth/                      # (manter - compartilhado)
└── shared-features/           # (criar)
    ├── scheduling/
    ├── chat/
    └── profile/
```

#### Etapa 1.2: Criar `shared-features/` para features compartilhadas

Features usadas por ambos os tipos de usuário devem ser movidas:

```bash
mkdir -p mobile/src/features/shared-features/{scheduling,profile,chat}

# Mover profile compartilhado
mv mobile/src/features/profile/* mobile/src/features/shared-features/profile/

# Mover scheduling compartilhado (lógica comum)
mv mobile/src/features/scheduling/* mobile/src/features/shared-features/scheduling/
```

#### Etapa 1.3: Atualizar imports e exports

Criar arquivos `index.ts` para cada módulo reorganizado e atualizar todos os imports nos arquivos que referenciam as features movidas.

#### Etapa 1.4: Mover Tab Navigators para suas features

```bash
# Mover StudentTabNavigator para student-app
mv mobile/src/navigation/StudentTabNavigator.tsx mobile/src/features/student-app/navigation/

# Mover InstructorTabNavigator para instructor-app
mv mobile/src/navigation/InstructorTabNavigator.tsx mobile/src/features/instructor-app/navigation/
```

**`RootNavigator.tsx` permanece em `navigation/`** pois é o ponto de entrada global.

---

### Fase 2: Reorganização Backend Use Cases (Prioridade Alta)

#### Etapa 2.1: Criar estrutura de pastas por tipo de usuário

```bash
mkdir -p backend/src/application/use_cases/{student,instructor,common}
```

#### Etapa 2.2: Categorizar e mover use cases existentes

**Para `student/`:**
- `search_instructors_by_location.py`
- `get_nearby_instructors.py`

**Para `instructor/`:**
- `update_instructor_profile.py`
- `update_instructor_location.py`

**Para `common/`:**
- `login_user.py`
- `logout_user.py`
- `register_user.py`
- `refresh_token.py`
- `reset_password.py`
- `update_student_profile.py` (renomear para `update_profile.py` genérico ou manter separado)

**Pastas existentes (manter):**
- `scheduling/` → mover para organização adequada ou manter se já está bem estruturado
- `payment/` → avaliar se é compartilhado ou separado
- `auth/` → mover para `common/`

#### Etapa 2.3: Atualizar imports e `__init__.py`

Atualizar todos os arquivos que importam use cases para refletir a nova estrutura.

---

### Fase 3: Reorganização Backend API Routes (Prioridade Média)

#### Etapa 3.1: Criar estrutura de routers por tipo de usuário

```bash
mkdir -p backend/src/interface/api/routers/{student,instructor,shared}
```

#### Etapa 3.2: Reorganizar routers existentes

**Para `student/`:**
- Mover lógica de busca de instrutores de `instructors.py`
- Criar `instructors.py` (busca de instrutores pelo aluno)
- Criar `lessons.py` (agendamentos do aluno)

**Para `instructor/`:**
- Mover lógica do perfil do instrutor
- Criar `availability.py`
- Criar `schedule.py`
- Criar `earnings.py`

**Para `shared/`:**
- `profile.py` (endpoints comuns)
- `notifications.py` (futuro)

**Manter na raiz:**
- `auth.py`
- `health.py`

#### Etapa 3.3: Atualizar prefixos de rotas

```python
# main.py
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(student_router, prefix="/api/v1/student")
app.include_router(instructor_router, prefix="/api/v1/instructor")
app.include_router(shared_router, prefix="/api/v1/shared")
```

---

### Fase 4: Implementar Guards de Permissão (Prioridade Alta)

#### Etapa 4.1: Criar guards em `dependencies.py`

```python
# backend/src/interface/api/dependencies.py

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

#### Etapa 4.2: Aplicar guards nos routers

Atualizar todos os endpoints para usar as dependencies apropriadas:

```python
@router.get("/search")
async def search_instructors(
    student: User = Depends(require_student),
    # ...
):
    pass

@router.get("/earnings")
async def get_earnings(
    instructor: User = Depends(require_instructor),
    # ...
):
    pass
```

---

### Fase 5: Atualizar Mobile API Layer (Prioridade Média)

#### Etapa 5.1: Reorganizar chamadas de API

Atualizar os arquivos de API no mobile para refletir os novos prefixos:

```typescript
// Antes
const response = await api.get('/instructors/search');

// Depois
const response = await api.get('/student/instructors/search');
```

#### Etapa 5.2: Organizar arquivos de API por feature

```plaintext
mobile/src/features/student-app/api/
├── instructors.ts      # Busca de instrutores
├── lessons.ts          # Agendamentos
└── index.ts

mobile/src/features/instructor-app/api/
├── availability.ts     # Disponibilidade
├── schedule.ts         # Agenda
├── earnings.ts         # Ganhos
└── index.ts
```

---

### Fase 6: Limpeza e Documentação (Prioridade Baixa)

#### Etapa 6.1: Remover pastas vazias

Após mover todos os arquivos, remover pastas antigas que ficaram vazias.

#### Etapa 6.2: Atualizar MOBILE_PLAN.md (se existir)

Refletir a nova estrutura no plano de desenvolvimento mobile.

#### Etapa 6.3: Criar arquivos README.md por feature

Documentar brevemente o propósito de cada feature:

```plaintext
mobile/src/features/student-app/README.md
mobile/src/features/instructor-app/README.md
mobile/src/features/shared-features/README.md
```

---

## Ordem de Execução Recomendada

| # | Fase | Risco | Esforço | Dependências |
|---|------|-------|---------|--------------|
| 1 | Fase 4: Guards de Permissão | Baixo | Baixo | Nenhuma |
| 2 | Fase 2: Backend Use Cases | Médio | Médio | Nenhuma |
| 3 | Fase 3: Backend API Routes | Alto | Alto | Fase 2 |
| 4 | Fase 1: Mobile Reorganização | Alto | Alto | Fase 3 |
| 5 | Fase 5: Mobile API Layer | Médio | Médio | Fases 3 e 4 |
| 6 | Fase 6: Limpeza | Baixo | Baixo | Todas |

> [!IMPORTANT]
> **Recomendação:** Executar as fases 4 e 2 primeiro, pois têm menor risco de quebrar funcionalidades existentes. As fases de reorganização de pastas (1, 3) devem ser feitas com cuidado, testando cada etapa.

---

## Checklist de Verificação

### Após cada fase:

- [ ] Aplicação mobile compila sem erros (`npx expo start`)
- [ ] Backend inicia sem erros (`docker compose up`)
- [ ] Testes existentes passam (se houver)
- [ ] Login funciona para ambos os tipos de usuário
- [ ] Navegação correta após login (aluno → StudentTab, instrutor → InstructorTab)

### Verificação Final:

- [ ] Estrutura de pastas conforme `PROJECT_GUIDELINES.md`
- [ ] Guards de permissão funcionando (testar acesso indevido)
- [ ] Todas as rotas com prefixos corretos
- [ ] Imports atualizados sem erros

---

## Estrutura Final Esperada

### Mobile

```plaintext
mobile/src/
├── features/
│   ├── student-app/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── navigation/StudentTabNavigator.tsx
│   ├── instructor-app/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── navigation/InstructorTabNavigator.tsx
│   ├── auth/
│   └── shared-features/
│       ├── scheduling/
│       ├── profile/
│       └── chat/
├── shared/
│   ├── components/
│   ├── hooks/
│   └── theme.ts
├── navigation/
│   └── RootNavigator.tsx
└── lib/
```

### Backend

```plaintext
backend/src/
├── application/
│   └── use_cases/
│       ├── student/
│       ├── instructor/
│       └── common/
├── interface/
│   └── api/
│       ├── routers/
│       │   ├── student/
│       │   ├── instructor/
│       │   └── shared/
│       └── dependencies.py  # com guards
├── domain/
└── infrastructure/
```
