# Plano de Refatoração: Filtros de Busca de Instrutores

## Objetivo

Implementar uma lógica de filtros profissional e funcional para busca de instrutores, corrigindo os problemas identificados na análise e seguindo padrões de apps de sucesso.

**Filtros em escopo:** Distância, Gênero, Categoria CNH

---

## Visão Geral das Fases

| Fase | Descrição | Prioridade | Estimativa |
|------|-----------|------------|------------|
| 1 | Correções críticas no backend | 🔴 Alta | 30 min |
| 2 | Integração frontend-backend | 🔴 Alta | 20 min |
| 3 | Filtros para instrutores sem localização | 🟠 Média | 20 min |
| 4 | Melhorias de UX | 🟡 Baixa | 15 min |

---

## Fase 1: Correções Críticas no Backend

### 1.1 Adicionar parâmetro `license_category` ao endpoint

**Arquivo:** `backend/src/interface/api/routers/student/instructors.py`

**Antes (linha 26-34):**
```python
async def search_instructors(
    latitude: float,
    longitude: float,
    instructor_repo: InstructorRepo,
    _current_student: CurrentStudent,
    radius_km: float = 10.0,
    biological_sex: str | None = None,
    limit: int = 50,
) -> InstructorSearchResponse:
```

**Depois:**
```python
async def search_instructors(
    latitude: float,
    longitude: float,
    instructor_repo: InstructorRepo,
    _current_student: CurrentStudent,
    radius_km: float = 10.0,
    biological_sex: str | None = None,
    license_category: str | None = None,  # NOVO
    limit: int = 50,
) -> InstructorSearchResponse:
```

**Atualizar criação do DTO (linha 41-48):**
```python
dto = InstructorSearchDTO(
    latitude=latitude,
    longitude=longitude,
    radius_km=radius_km,
    biological_sex=biological_sex,
    license_category=license_category,  # NOVO
    only_available=True,
    limit=limit,
)
```

---

### 1.2 Adicionar campo `license_category` ao DTO

**Arquivo:** `backend/src/application/dtos/profile_dtos.py`

**Antes (linha 51-59):**
```python
@dataclass(frozen=True)
class InstructorSearchDTO:
    latitude: float
    longitude: float
    radius_km: float = 10.0
    biological_sex: str | None = None
    only_available: bool = True
    limit: int = 50
```

**Depois:**
```python
@dataclass(frozen=True)
class InstructorSearchDTO:
    latitude: float
    longitude: float
    radius_km: float = 10.0
    biological_sex: str | None = None
    license_category: str | None = None  # NOVO
    only_available: bool = True
    limit: int = 50
```

---

### 1.3 Passar parâmetros ao Repository

**Arquivo:** `backend/src/application/use_cases/student/get_nearby_instructors.py`

**Antes (linha 106-112):**
```python
profiles_with_location = await self.instructor_repository.search_by_location(
    center=center,
    radius_km=dto.radius_km,
    only_available=dto.only_available,
    limit=dto.limit,
)
```

**Depois:**
```python
profiles_with_location = await self.instructor_repository.search_by_location(
    center=center,
    radius_km=dto.radius_km,
    biological_sex=dto.biological_sex,        # NOVO
    license_category=dto.license_category,    # NOVO
    only_available=dto.only_available,
    limit=dto.limit,
)
```

---

### 1.4 Adicionar filtro de categoria ao Repository

**Arquivo:** `backend/src/infrastructure/repositories/instructor_repository_impl.py`

**Antes (linha 100-107):**
```python
async def search_by_location(
    self,
    center: Location,
    radius_km: float = 10.0,
    biological_sex: str | None = None,
    only_available: bool = True,
    limit: int = 50,
) -> list[InstructorProfile]:
```

**Depois:**
```python
async def search_by_location(
    self,
    center: Location,
    radius_km: float = 10.0,
    biological_sex: str | None = None,
    license_category: str | None = None,  # NOVO
    only_available: bool = True,
    limit: int = 50,
) -> list[InstructorProfile]:
```

**Adicionar filtro após linha 155:**
```python
if biological_sex:
    from src.infrastructure.db.models.user_model import UserModel
    stmt = stmt.where(UserModel.biological_sex == biological_sex)

# NOVO: Filtro por categoria CNH
if license_category:
    stmt = stmt.where(InstructorProfileModel.license_category == license_category)
```

---

### 1.5 Atualizar Interface do Repository

**Arquivo:** `backend/src/domain/interfaces/instructor_repository.py`

**Antes (linha 87-94):**
```python
async def search_by_location(
    self,
    center: Location,
    radius_km: float = 10.0,
    biological_sex: str | None = None,
    only_available: bool = True,
    limit: int = 50,
) -> list[InstructorProfile]:
```

**Depois:**
```python
async def search_by_location(
    self,
    center: Location,
    radius_km: float = 10.0,
    biological_sex: str | None = None,
    license_category: str | None = None,  # NOVO
    only_available: bool = True,
    limit: int = 50,
) -> list[InstructorProfile]:
```

---

## Fase 2: Integração Frontend-Backend

### 2.1 Enviar parâmetro `category` na API

**Arquivo:** `mobile/src/features/student-app/search/api/searchApi.ts`

**Antes (linha 56-71):**
```typescript
export async function searchInstructors(
    params: SearchInstructorsParams
): Promise<SearchInstructorsResponse> {
    const { latitude, longitude, radiusKm = 10, limit = 50, biological_sex } = params;

    const response = await api.get<SearchInstructorsResponse>(`${STUDENT_API}/instructors/search`, {
        params: {
            latitude,
            longitude,
            radius_km: radiusKm,
            limit,
            biological_sex,
        },
    });
```

**Depois:**
```typescript
export async function searchInstructors(
    params: SearchInstructorsParams
): Promise<SearchInstructorsResponse> {
    const { latitude, longitude, radiusKm = 10, limit = 50, biological_sex, category } = params;

    const response = await api.get<SearchInstructorsResponse>(`${STUDENT_API}/instructors/search`, {
        params: {
            latitude,
            longitude,
            radius_km: radiusKm,
            limit,
            biological_sex,
            license_category: category,  // Mapeia 'category' para 'license_category'
        },
    });
```

---

## Fase 3: Filtros para Instrutores sem Localização

### 3.1 Adicionar parâmetros ao método `get_available_instructors`

**Arquivo:** `backend/src/infrastructure/repositories/instructor_repository_impl.py`

**Antes (linha 202-214):**
```python
async def get_available_instructors(self, limit: int = 100) -> list[InstructorProfile]:
    """Lista instrutores disponíveis."""
    stmt = (
        select(
            InstructorProfileModel,
            geo_func.ST_X(InstructorProfileModel.location).label("lon"),
            geo_func.ST_Y(InstructorProfileModel.location).label("lat"),
        )
        .where(InstructorProfileModel.is_available.is_(True))
        .options(joinedload(InstructorProfileModel.user))
        .order_by(InstructorProfileModel.rating.desc())
        .limit(limit)
    )
```

**Depois:**
```python
async def get_available_instructors(
    self,
    biological_sex: str | None = None,
    license_category: str | None = None,
    limit: int = 100,
) -> list[InstructorProfile]:
    """Lista instrutores disponíveis com filtros opcionais."""
    stmt = (
        select(
            InstructorProfileModel,
            geo_func.ST_X(InstructorProfileModel.location).label("lon"),
            geo_func.ST_Y(InstructorProfileModel.location).label("lat"),
        )
        .join(InstructorProfileModel.user)
        .where(InstructorProfileModel.is_available.is_(True))
        .options(joinedload(InstructorProfileModel.user))
        .order_by(InstructorProfileModel.rating.desc())
        .limit(limit)
    )

    if biological_sex:
        from src.infrastructure.db.models.user_model import UserModel
        stmt = stmt.where(UserModel.biological_sex == biological_sex)

    if license_category:
        stmt = stmt.where(InstructorProfileModel.license_category == license_category)
```

---

### 3.2 Atualizar chamada no Use Case

**Arquivo:** `backend/src/application/use_cases/student/get_nearby_instructors.py`

**Antes (linha 114-117):**
```python
all_available = await self.instructor_repository.get_available_instructors(
    limit=dto.limit,
)
```

**Depois:**
```python
all_available = await self.instructor_repository.get_available_instructors(
    biological_sex=dto.biological_sex,
    license_category=dto.license_category,
    limit=dto.limit,
)
```

---

### 3.3 Atualizar Interface do Repository

**Arquivo:** `backend/src/domain/interfaces/instructor_repository.py`

**Antes (linha 125-136):**
```python
@abstractmethod
async def get_available_instructors(self, limit: int = 100) -> list[InstructorProfile]:
```

**Depois:**
```python
@abstractmethod
async def get_available_instructors(
    self,
    biological_sex: str | None = None,
    license_category: str | None = None,
    limit: int = 100,
) -> list[InstructorProfile]:
```

---

## Fase 4: Melhorias de UX

### 4.1 Corrigir indicador de filtro ativo

**Arquivo:** `mobile/src/features/student-app/search/screens/InstructorSearchScreen.tsx`

**Antes (linha 117-118):**
```typescript
{FILTER_CHIPS.map((chip, index) => {
    const isActive = index === 0 && hasActiveFilters;
```

**Depois:**
```typescript
{FILTER_CHIPS.map((chip) => {
    // Verificar se o filtro específico deste chip está ativo
    const isActive = chip.key === 'category' 
        ? !!filters.category 
        : chip.key === 'biological_sex' 
            ? !!filters.biological_sex 
            : false;
```

---

### 4.2 Adicionar opção "Qualquer Distância"

**Arquivo:** `mobile/src/features/student-app/search/components/FilterModal.tsx`

**Antes (linha 21):**
```typescript
const DISTANCE_OPTIONS = [5, 10, 20, 50];
```

**Depois:**
```typescript
const DISTANCE_OPTIONS = [
    { value: 5, label: '5 km' },
    { value: 10, label: '10 km' },
    { value: 20, label: '20 km' },
    { value: 50, label: '50 km' },
    { value: undefined, label: 'Qualquer' },
];
```

> [!NOTE]
> Atualizar renderização (linha 115-138) para usar o novo formato de objeto.

---

## Verificação

### Testes Manuais

1. **Filtro de Categoria CNH:**
   - [ ] Selecionar categoria "B" → Apenas instrutores com CNH B aparecem
   - [ ] Limpar filtro → Todos instrutores aparecem

2. **Filtro de Gênero:**
   - [ ] Selecionar "Feminino" → Apenas instrutoras aparecem
   - [ ] Verificar que instrutores SEM localização também são filtrados

3. **Filtro de Distância:**
   - [ ] Selecionar 5km → Apenas instrutores a 5km aparecem
   - [ ] Selecionar "Qualquer" → Todos aparecem (inclui sem localização)

4. **Combinação de Filtros:**
   - [ ] Categoria B + Feminino → Apenas instrutoras com CNH B
   - [ ] Distância 10km + Masculino → Apenas instrutores masculinos a 10km

---

## Checklist de Arquivos

| Arquivo | Fase | Status |
|---------|------|--------|
| `backend/.../instructors.py` | 1 | [ ] |
| `backend/.../profile_dtos.py` | 1 | [ ] |
| `backend/.../get_nearby_instructors.py` | 1, 3 | [ ] |
| `backend/.../instructor_repository_impl.py` | 1, 3 | [ ] |
| `backend/.../instructor_repository.py` | 1, 3 | [ ] |
| `mobile/.../searchApi.ts` | 2 | [ ] |
| `mobile/.../InstructorSearchScreen.tsx` | 4 | [ ] |
| `mobile/.../FilterModal.tsx` | 4 | [ ] |
