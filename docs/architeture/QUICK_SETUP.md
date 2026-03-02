# GoDrive - Configuração Rápida (Quick Setup)

Este guia descreve como configurar e rodar o projeto GoDrive (Backend e Mobile) em seu ambiente local.

## Pré-requisitos

Certifique-se de ter as seguintes ferramentas instaladas:

- **Docker** e **Docker Compose** (Para banco de dados e Redis)
- **Node.js** (v18 ou superior)
- **Python** (v3.10 ou superior)
- **Git**

---

## 🚀 Início Rápido (Infraestrutura)

A maneira mais fácil de iniciar a infraestrutura base (PostgreSQL + PostGIS e Redis) e o Backend é utilizando o Docker.

1. **Subir os serviços**:
   Na raiz do projeto, execute:
   ```bash
   docker compose up -d --build
   ```

   Isso iniciará:
   - **PostgreSQL**: Porta `5432`
   - **Redis**: Porta `6379`
   - **Backend API**: Porta `8000`

2. **Verificar o Backend**:
   Acesse a documentação da API em: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📱 Configuração do Mobile

O aplicativo mobile deve ser executado localmente fora do Docker para facilitar o desenvolvimento com o Expo.

1. **Navegue até a pasta mobile**:
   ```bash
   cd mobile
   ```

2. **Instale as dependências**:
   ```bash
   npm install
   ```

3. **Inicie o servidor de desenvolvimento**:
   ```bash
   npx expo start --dev-client
   ```
   ou
   ```bash
   npx expo start --dev-client --tunnel -c
   ```
   
   - Pressione `a` para abrir no emulador Android.
   - Pressione `i` para abrir no simulador iOS (macOS apenas).
   - Use o aplicativo **Expo Go** no seu celular para escanear o QR Code.

---

## 🛠️ Setup Manual do Backend (Opcional)

Caso prefira rodar o Backend fora do Docker (para debugging avançado), siga estes passos:

1. **Certifique-se que o Banco e Redis estão rodando** (via docker-compose):
   ```bash
   docker compose up -d postgres redis
   ```

2. **Navegue até a pasta backend**:
   ```bash
   cd backend
   ```

3. **Crie e ative um ambiente virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   ```

4. **Instale as dependências**:
   ```bash
   pip install -e ".[dev]"
   ```

5. **Execute as migrações do banco de dados**:
   ```bash
   alembic upgrade head
   ```

6. **Inicie o servidor**:
   ```bash
   uvicorn src.interface.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## ✅ Comandos Úteis

### Verificação de Código (Linting & Formatting)

**Backend:**
```bash
# Na pasta backend/
ruff check .           # Lint
ruff format .          # Format
```

**Mobile:**
```bash
# Na pasta mobile/
npm run lint           # Lint
```

### Testes

**Backend:**
```bash
# Na pasta backend/
pytest
```

**Pré-commit:**
Para garantir qualidade antes de enviar alterações:
```bash
pre-commit run --all-files
```
