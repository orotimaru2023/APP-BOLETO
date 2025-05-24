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

EXPOSE 8000

# Criar script de inicialização
RUN echo '#!/bin/sh\n\
PORT="${PORT:-8000}"\n\
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers 4\n\
' > /app/start.sh && chmod +x /app/start.sh

# Usar script de inicialização
CMD ["/bin/sh", "/app/start.sh"] 