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

# Configurar variáveis de ambiente básicas
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Valores padrão para desenvolvimento local
ENV PORT=8000
ENV ENVIRONMENT=development
ENV DATABASE_URL=sqlite:///./app.db
ENV ACCESS_TOKEN_EXPIRE_MINUTES=60
ENV ALGORITHM=HS256
ENV SECRET_KEY=dev_secret_key_do_not_use_in_production

EXPOSE 8000

# Criar script de inicialização
RUN echo '#!/bin/bash\n\
# Aguardar 5 segundos para o banco de dados inicializar\n\
sleep 5\n\
# Inicializar o banco de dados\n\
python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)"\n\
# Configurar a porta\n\
if [ -z "$PORT" ]; then\n\
    PORT=8000\n\
fi\n\
# Iniciar o servidor\n\
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4 --log-level info\n\
' > /app/start.sh && chmod +x /app/start.sh

# Usar script de inicialização
CMD ["/bin/bash", "/app/start.sh"] 