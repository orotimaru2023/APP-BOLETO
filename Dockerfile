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

# Verificar a estrutura do projeto
RUN ls -la /code && ls -la /code/app

EXPOSE 8000

# Criar arquivo Python para inicialização
RUN echo 'import os\n\
import uvicorn\n\
from app.db import Base, engine\n\
from app.models import *\n\
\n\
def init_db():\n\
    print("Inicializando banco de dados...")\n\
    Base.metadata.create_all(bind=engine)\n\
\n\
def main():\n\
    port = int(os.getenv("PORT", "8000"))\n\
    init_db()\n\
    print(f"Iniciando servidor na porta {port}...")\n\
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, workers=1, log_level="debug")\n\
\n\
if __name__ == "__main__":\n\
    main()\n\
' > /code/start.py

# Usar Python diretamente para inicialização
CMD ["python", "start.py"] 