# GoDrive Backend - Dockerfile
# Python 3.10+ para desenvolvimento

FROM python:3.10-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema para asyncpg e PostGIS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 8000

# Comando padrão (sobrescrito no docker-compose para hot-reload)
CMD ["uvicorn", "src.interface.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
