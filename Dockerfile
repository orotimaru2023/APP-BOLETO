FROM python:3.10-slim

WORKDIR /code

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas os arquivos necessários primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Criar estrutura de diretórios e copiar arquivos
COPY . .

# Configurar variáveis de ambiente
ENV PYTHONPATH=/code
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV ENVIRONMENT=production
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
ls -la app/\n\
\n\
echo "Aguardando banco de dados..."\n\
sleep 5\n\
\n\
echo "Inicializando banco de dados..."\n\
PYTHONPATH=/code python3 -c "from app.db import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine)"\n\
\n\
echo "Configurando porta..."\n\
PORT="${PORT:-8000}"\n\
\n\
echo "Iniciando servidor na porta $PORT..."\n\
PYTHONPATH=/code exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers 1 --log-level debug\n\
' > /code/start.sh && chmod +x /code/start.sh

# Usar script de inicialização
CMD ["/bin/bash", "/code/start.sh"] 