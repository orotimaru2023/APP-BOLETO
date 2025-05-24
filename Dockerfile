FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas os arquivos necessários primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos
COPY app/ app/

# Configurar variáveis de ambiente
ENV PYTHONPATH=/app
ENV PORT=8000
ENV ENVIRONMENT=production
ENV PYTHONUNBUFFERED=1

EXPOSE ${PORT}

# Usar o módulo correto com shell form para permitir expansão de variáveis
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4 