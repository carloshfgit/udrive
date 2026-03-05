# Refatoração e Customização do SQLAdmin

Este documento define a estratégia arquitetural, melhores práticas de organização e os passos iniciais necessários para prepararmos o terreno para as customizações avançadas do **SQLAdmin** no painel de administração do GoDrive.

## 1. Estado Atual da Arquitetura do SQLAdmin
Atualmente, a interface administrativa encontra-se na camada de interface (`src/interface/admin/`) e possui os seguintes arquivos:
- `__init__.py`: Configuração e inicialização principal (`Setup Admin`).
- `auth.py`: Autenticação básica via sessão e verificação de privilégio `UserType.ADMIN`.
- `views.py`: Concentra todas as representações (ModelViews) do banco de dados (`UserAdmin`, `InstructorProfileAdmin`, `StudentProfileAdmin`, `SchedulingAdmin`, `DisputeAdmin`).

**Problema atual:** À medida que adicionarmos "Ações Customizadas" (ex: Resolver Disputa, Banir Usuário) e "Templates Customizados", o arquivo `views.py` vai inchar rapidamente, misturando lógicas de múltiplos domínios e ferindo o princípio de responsabilidade única (SRP). Além disso, não temos um local designado para injetar comportamento de negócio (Use Cases) e overrides de HTML.

## 2. Melhores Práticas de Arquitetura, Organização e Segurança

No contexto de Clean Architecture, o *admin* atua como um "Detail" ou "Delivery Mechanism" (como a API REST). Portanto, ele **não deve** conter regra de negócio; ele deve apenas chamar os Casos de Uso (Use Cases) existentes.

### Organização de Diretórios Proposta
Sugerimos refatorar o diretório `src/interface/admin/` para a seguinte estrutura:

```text
src/interface/admin/
├── __init__.py            # Inicialização e registro de todas as views
├── auth.py                # Mantém a autenticação do Admin
├── templates/             # NOVO: Diretório para templates Jinja2 customizados (overrides)
│   ├── custom_list.html
│   └── custom_details.html
└── views/                 # NOVO: Diretório para separar as ModelViews por domínio
    ├── __init__.py
    ├── user_views.py      # UserAdmin, InstructorProfileAdmin, StudentProfileAdmin
    ├── scheduling_views.py# SchedulingAdmin
    └── dispute_views.py   # DisputeAdmin (Aqui entrarão as Actions de Disputa)
```

### Regras de Segurança e Boas Práticas
1. **Delegação de Lógica**: Funções anotadas com `@action` no SQLAdmin **devem** ser delegadas imediatamente para a camada de *Application*. Por exemplo, o botão "Resolver Disputa" receberá os dados do request e acionará `ResolveDisputeUseCase().execute(...)`.
2. **Trilhas de Auditoria (Audit Logging)**: O `auth.py` armazena o `user_id` na sessão. Todas as ações customizadas que modificarem dados no Admin devem recuperar este `admin_id` da sessão e repassá-lo ao Use Case (ou registrar um log) indicando quem realizou a modificação.
3. **Template Injection**: O SQLAdmin procurará os templates customizados na pasta `templates/`. Devemos evitar colocar lógica pesada no Jinja2, priorizando apresentar os dados limpos entregues pela query ou campos formatados.
4. **Gerenciamento de Transações**: Por rodar em ASGI com Starlette, devemos garantir que cada ação customizada do backend abra e feche sua sessão de banco via o mesmo `AsyncSessionLocal` do FastAPI, prevenindo vazamentos de conexões.

## 3. Passos para a Refatoração (O que mudar no sistema)

Para preparar o terreno, precisamos realizar as seguintes mudanças no código fonte atual:

### Passo 1: Configurar a Pasta de Templates
No arquivo `src/interface/admin/__init__.py`, registrar o diretório onde o SQLAdmin lerá templates customizados:
```python
import os
from sqladmin import Admin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")

admin = Admin(
    app=app,
    engine=engine,
    authentication_backend=authentication_backend,
    title="GoDrive Admin",
    templates_dir=templates_dir, # <-- NOVA LINHA
)
```

### Passo 2: Criar o Diretório de `views/` e Desmembrar `views.py`
Excluir o arquivo monolítico `views.py` e separá-lo logicamente dentro de `src/interface/admin/views/`. 
- `user_views.py`
- `scheduling_views.py`
- `dispute_views.py`

### Passo 3: Criar Base Views (Opcional, mas Recomendado)
Criar uma classe `BaseAdminView(ModelView)` central, caso todos os modelos necessitem das mesmas configurações globais (por exemplo, tamanho da página `page_size`, formatação global de data, etc).

### Passo 4: Implementar Tratadores de Sessão Básicos nas Ações
Uma vez refatorado, criar o esqueleto básico nas Actions (ex: em `dispute_views.py`) demonstrando como obter a sessão assíncrona para chamar os Use Cases:

```python
from sqladmin import action
from starlette.requests import Request
from starlette.responses import RedirectResponse
from src.infrastructure.db.database import AsyncSessionLocal
from src.application.use_cases.dispute.resolve_dispute import ResolveDisputeUseCase
# ...

class DisputeAdmin(ModelView, model=DisputeModel):
    # ... configurações de colunas ...

    @action(name="resolve_dispute", label="Resolver Disputa", confirmation_message="Tem certeza?")
    async def resolve_dispute(self, request: Request):
        pks = request.query_params.get("pks", "").split(",")
        admin_id = request.session.get("user_id")
        
        async with AsyncSessionLocal() as db_session:
            # Chama o use case para todos os selecionados
            pass
            
        return RedirectResponse(request.url_for("admin:list", identity=self.identity), status_code=302)
```

## Conclusão
Executando os Passos 1 e 2, o sistema sairá do amadorismo visual/arquitetural, tornando as ModelViews dezenas de vezes mais limpas e prontas para receber os templates de *Tailwind* ou lógicas com ações sem intervir na API pública do aplicativo mobile.
