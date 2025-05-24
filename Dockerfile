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
COPY app/ .

# Configurar variáveis de ambiente básicas
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Valores padrão para desenvolvimento local
ENV PORT=8000
ENV ENVIRONMENT=development
ENV DATABASE_URL=sqlite:///./app.db
ENV ACCESS_TOKEN_EXPIRE_MINUTES=60
ENV ALGORITHM=HS256
ENV SECRET_KEY=minha_super_chave_secreta_padrao_nao_usar_em_producao

EXPOSE 8000

# Criar script de inicialização
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Verificando estrutura do projeto..."\n\
ls -la\n\
\n\
echo "Aguardando banco de dados..."\n\
sleep 5\n\
\n\
echo "Inicializando banco de dados..."\n\
PYTHONPATH=/app python3 -c "from db import Base, engine; Base.metadata.create_all(bind=engine)"\n\
\n\
echo "Configurando porta..."\n\
PORT="${PORT:-8000}"\n\
\n\
echo "Iniciando servidor na porta $PORT..."\n\
PYTHONPATH=/app exec python3 -m uvicorn main:app --host 0.0.0.0 --port "$PORT" --workers 4 --log-level info\n\
' > /app/start.sh && chmod +x /app/start.sh

# Usar script de inicialização
CMD ["/bin/bash", "/app/start.sh"] 