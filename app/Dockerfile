FROM python:3.10-slim

WORKDIR /app

# Copiar apenas os arquivos necessários primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto dos arquivos
COPY . .

# Configurar variáveis de ambiente
ENV PYTHONPATH=/app
ENV PORT=8000

EXPOSE 8000

# Usar o módulo correto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
